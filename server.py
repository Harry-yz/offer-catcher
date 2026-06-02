"""
Offer Catcher - Flask后端
支持本地运行和1Panel子目录部署
"""

from flask import Flask, render_template, request, jsonify
import json
import os
import traceback
from dotenv import load_dotenv

BASE_DIR = os.environ.get('ROOT_DIR', os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path, override=True)

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

from api import api, parse_text, pdf_to_text
from parser import parse_resume_from_dict, parse_jd_from_dict, do_parse_resume, do_parse_jd
from config import PARSE_RESUME_PROMPT, PARSE_JD_PROMPT, SHIELD_PROMPT, SPEAR_PROMPT

MATCH_AGENT_PROMPT = """你是一位资深HR顾问，擅长精准匹配候选人与岗位。
## 任务
分析候选人简历与目标岗位的匹配程度。
## 输出要求
必须严格按照以下JSON格式输出，score字段必须存在且为0-100的整数：
{
  "score": 75,
  "matched": ["匹配点1：具体说明"],
  "unmatched": ["不匹配点1：具体说明"],
  "optimization": ["优化建议1：具体可操作"],
  "summary": "一句话总结匹配情况"
}
"""

REPORT_AGENT_PROMPT = """你是一位招聘报告撰写专家。
任务：将多个匹配结果排序，生成报告。
输出JSON格式：
{
  "ranked_results": [
    {
      "rank": 1, "company": "公司", "position": "职位", "location": "地点",
      "score": 85, "matched": ["匹配点1"], "unmatched": ["不匹配点1"],
      "optimization": ["优化建议1"], "summary": "一句话总结"
    }
  ],
  "overall_summary": "综合分析"
}
排序规则：按score从高到低排序"""

@app.route('/')
@app.route('/offercatcher/')  # 增加这一行，让它同时适配根目录和子目录请求
def index():
    return render_template('index.html')

@app.route('/seeker')
def seeker():
    return render_template('workbench.html', mode='seeker')

@app.route('/interview')
def interview():
    return render_template('workbench_interview.html')

@app.route('/interviewer')
def interviewer():
    return render_template('workbench.html', mode='interviewer')

@app.route('/api/parse', methods=['POST'])
@app.route('/offercatcher/api/parse', methods=['POST'])
def api_parse():
    try:
        resume_file = request.files.get('resume')
        if not resume_file:
            return jsonify({'error': '请上传简历'}), 400
        resume_bytes = resume_file.read()
        
        class FileWrapper:
            def __init__(self, data, name):
                self._data = data
                self.name = name
            def read(self): return self._data
        
        resume = do_parse_resume(FileWrapper(resume_bytes, resume_file.filename))
        if not resume:
            return jsonify({'error': '简历解析失败'}), 400
        
        jds = []
        jd_files = request.files.getlist('jd_files')
        jd_texts = request.form.getlist('jd_texts')
        
        for jd_file in jd_files:
            if jd_file and jd_file.filename:
                jd = do_parse_jd(FileWrapper(jd_file.read(), jd_file.filename))
                if jd:
                    jds.append({
                        'company': jd.company, 'position': jd.position, 'location': jd.location,
                        'requirements': {
                            'must_have': [{'skill': r.skill, 'importance': r.importance} for r in jd.requirements.must_have],
                            'nice_to_have': [{'skill': r.skill, 'importance': r.importance} for r in jd.requirements.nice_to_have]
                        },
                        'responsibilities': jd.responsibilities
                    })
        
        for jd_text in jd_texts:
            if jd_text and jd_text.strip():
                jd = do_parse_jd(text_input=jd_text)
                if jd:
                    jds.append({
                        'company': jd.company, 'position': jd.position, 'location': jd.location,
                        'requirements': {
                            'must_have': [{'skill': r.skill, 'importance': r.importance} for r in jd.requirements.must_have],
                            'nice_to_have': [{'skill': r.skill, 'importance': r.importance} for r in jd.requirements.nice_to_have]
                        },
                        'responsibilities': jd.responsibilities
                    })
        
        if not jds:
            return jsonify({'error': '请至少上传一个JD（图片或文本）'}), 400
        
        resume_data = {
            'name': resume.name,
            'education': {'school': resume.education.school, 'major': resume.education.major, 'degree': resume.education.degree},
            'skills': resume.skills,
            'projects': [{'name': p.name, 'description': p.description, 'key_achievements': p.key_achievements, 'technologies': p.technologies} for p in resume.projects]
        }
        return jsonify({'success': True, 'resume': resume_data, 'jds': jds})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'解析失败: {str(e)}'}), 500

@app.route('/api/match', methods=['POST'])
@app.route('/offercatcher/api/match', methods=['POST'])
def api_match():
    try:
        data = request.json
        resume = data.get('resume')
        jds = data.get('jds', [])
        
        if not resume or not jds:
            return jsonify({'error': '缺少简历或JD数据'}), 400
        
        match_results = []
        failed_jds = []
        for jd in jds:
            company = jd.get('company', '未知公司')
            position = jd.get('position', '未知职位')
            user_prompt = f"请分析候选人与岗位的匹配度：\n## 候选人简历\n{json.dumps(resume, ensure_ascii=False)}\n## 目标岗位\n{json.dumps(jd, ensure_ascii=False)}"

            try:
                result = api([{"role": "system", "content": MATCH_AGENT_PROMPT}, {"role": "user", "content": user_prompt}], json_mode=True)
                if result and isinstance(result, dict) and 'score' in result:
                    result['company'] = company
                    result['position'] = position
                    result['location'] = jd.get('location', '')
                    result['score'] = int(result['score']) if str(result['score']).isdigit() else 50
                    match_results.append(result)
                else:
                    failed_jds.append(f"{company} - {position} (API未返回score)")
            except Exception as e:
                failed_jds.append(f"{company} - {position} (请求报错: {str(e)})")
        
        if not match_results:
            return jsonify({'error': f'匹配阶段全部失败，失败详情: {", ".join(failed_jds)}'}), 400
        
        report_prompt = f"请对以下匹配结果进行排序，生成最终报告：\n{json.dumps(match_results, ensure_ascii=False)}"
        try:
            report = api([{"role": "system", "content": REPORT_AGENT_PROMPT}, {"role": "user", "content": report_prompt}], json_mode=True)
        except Exception as e:
            report = None
            
        if not report:
            report = {"ranked_results": sorted(match_results, key=lambda x: x.get('score', 0), reverse=True), "overall_summary": "综合分析生成超时，已返回基础排序结果。"}
        
        return jsonify({'success': True, 'result': report})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f"内部错误: {str(e)}"}), 500

@app.route('/api/interview', methods=['POST'])
@app.route('/offercatcher/api/interview', methods=['POST'])
def api_interview():
    try:
        data = request.json
        resume = data.get('resume')
        jd = data.get('jd')
        match_result = data.get('match_result', {})
        mode = data.get('mode', 'shield')
        
        system_prompt = SHIELD_PROMPT if mode == "shield" else SPEAR_PROMPT
        
        # 【核心修复1】简化提示词，减少生成时间
        json_schema = """
        严格按以下JSON格式输出：
        {
          "self_intro": {
            "formal": "一段专业的自我介绍（100-150字）",
            "key_points": ["核心亮点1", "核心亮点2"]
          },
          "questions": [
            {"question": "面试问题1", "intent": "考察点", "answer": "参考答案", "follow_ups": ["追问1"]},
            {"question": "面试问题2", "intent": "考察点", "answer": "参考答案", "follow_ups": ["追问1"]},
            {"question": "面试问题3", "intent": "考察点", "answer": "参考答案", "follow_ups": ["追问1"]},
            {"question": "面试问题4", "intent": "考察点", "answer": "参考答案", "follow_ups": ["追问1"]},
            {"question": "面试问题5", "intent": "考察点", "answer": "参考答案", "follow_ups": ["追问1"]}
          ]
        }
        注意：自我介绍控制在150字以内，每道题的答案控制在100字以内。
        """
        
        if mode == "shield":
            matched = [m if isinstance(m, str) else m.get('requirement', '') for m in match_result.get('matched', [])[:3]]
            missing = [m if isinstance(m, str) else m.get('requirement', '') for m in match_result.get('unmatched', match_result.get('missing', []))[:2]]
            user_prompt = f"【候选人简历】\n{json.dumps(resume, ensure_ascii=False)}\n【目标岗位】\n{json.dumps(jd, ensure_ascii=False)}\n【匹配优势】\n{matched}\n【能力缺失】\n{missing}\n\n{json_schema}"
        else:
            user_prompt = f"【候选人简历】\n{json.dumps(resume, ensure_ascii=False)}\n【目标岗位】\n{json.dumps(jd, ensure_ascii=False)}\n\n{json_schema}"

        result = api([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], json_mode=True)
        
        if not result:
            result = {"self_intro": {"formal": "生成超时，暂无", "key_points": []}, "questions": []}
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f"面试策略生成失败: {str(e)}"}), 500

@app.route('/api/mock', methods=['POST'])
@app.route('/offercatcher/api/mock', methods=['POST'])
def api_mock():
    try:
        data = request.json
        history = data.get('history', [])
        question = data.get('question', '')
        answer = data.get('answer', '')
        mode = data.get('mode', 'shield')
        
        system = SHIELD_PROMPT if mode == "shield" else SPEAR_PROMPT
        
        # 【核心修复2】去除了 next_question 的生成逻辑，全神贯注写反馈
        prompt = """作为资深面试官，请根据候选人的回答进行专业评分，指出具体不足（反馈），并给出你期待的标准答案。
        严格按此JSON格式输出：
        {
          "scores": {
            "technical_depth": 70,
            "quantitative_support": 80,
            "logical_clarity": 85
          },
          "overall": 78,
          "feedback": "指出回答的闪光点以及具体的改进建议...",
          "model_answer": "遇到这类问题，高分的回答框架应该是：..."
        }
        """
        
        msgs = [{"role": "system", "content": system + "\n\n" + prompt}]
        for h in history[-4:]:
            msgs.append({"role": h["role"], "content": h["content"]})
        msgs.append({"role": "user", "content": f"当前面试题：{question}\n\n候选人回答：{answer}"})
        
        result = api(msgs, json_mode=True)
        if not result:
            result = {"scores": {"technical_depth": 60, "quantitative_support": 60, "logical_clarity": 60}, "overall": 60, "feedback": "回答已记录，API生成点评超时", "model_answer": "暂无"}
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/mineru', methods=['GET'])
@app.route('/offercatcher/api/debug/mineru', methods=['GET'])
def debug_mineru():
    """检查MinerU配置状态"""
    from mineru_parser import is_available, MINERU_API_KEY, mineru_parser
    return jsonify({
        'mineru_available': is_available(),
        'api_key_configured': bool(MINERU_API_KEY),
        'api_key_prefix': MINERU_API_KEY[:10] + '...' if MINERU_API_KEY else 'None',
        'base_url': mineru_parser.base_url
    })

@app.route('/api/debug/test-mineru', methods=['GET'])
@app.route('/offercatcher/api/debug/test-mineru', methods=['GET'])
def test_mineru():
    """测试MinerU连通性"""
    import requests
    from mineru_parser import MINERU_API_KEY
    try:
        url = "https://mineru.net/api/v4/file-urls/batch"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MINERU_API_KEY}"
        }
        data = {"files": [{"name": "test.txt"}], "model_version": "vlm"}
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        return jsonify({
            'status_code': resp.status_code,
            'response': resp.text[:500]
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)