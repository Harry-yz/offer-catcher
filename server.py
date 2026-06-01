# server.py
"""
Offer Catcher - Flask后端
支持本地运行和Vercel部署
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)

# 获取项目根目录
BASE_DIR = os.environ.get('ROOT_DIR', os.path.dirname(os.path.abspath(__file__)))

# 创建Flask应用
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

# 设置最大内容长度 (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 确保模板目录存在
if not os.path.exists(os.path.join(BASE_DIR, 'templates')):
    os.makedirs(os.path.join(BASE_DIR, 'templates'), exist_ok=True)

# ============================================================
# API层
# ============================================================
from api import api, parse_text, pdf_to_text
from parser import parse_resume_from_dict, parse_jd_from_dict, do_parse_resume, do_parse_jd
from config import PARSE_RESUME_PROMPT, PARSE_JD_PROMPT, SHIELD_PROMPT, SPEAR_PROMPT

# ============================================================
# Agent Prompt定义
# ============================================================

MATCH_AGENT_PROMPT = """你是一位资深HR顾问，擅长精准匹配候选人与岗位。

## 任务
分析候选人简历与目标岗位的匹配程度。

## 输出要求
必须严格按照以下JSON格式输出，score字段必须存在且为0-100的整数：

```json
{
  "score": 75,
  "matched": ["匹配点1：具体说明", "匹配点2：具体说明"],
  "unmatched": ["不匹配点1：具体说明", "不匹配点2：具体说明"],
  "optimization": ["优化建议1：具体可操作", "优化建议2：具体可操作"],
  "summary": "一句话总结匹配情况"
}
```

## 评分标准
- 90-100：高度匹配，强烈推荐
- 70-89：较好匹配，建议面试
- 50-69：一般匹配，可考虑
- 0-49：匹配度低，不建议

## 评分规则
- 精确匹配（100%）：技能名称完全匹配
- 模糊匹配（80%）：技能包含关系（如Python包含Python3）
- 相关匹配（60%）：技术栈关联（如Django和Python相关）

## 重要提醒
1. score字段必须存在，值为0-100的整数
2. matched和unmatched数组不能为空
3. summary必须是一句话总结
4. 输出必须是有效的JSON格式"""

REPORT_AGENT_PROMPT = """你是一位招聘报告撰写专家。

任务：将多个匹配结果排序，生成报告。

输出JSON格式：
{
  "ranked_results": [
    {
      "rank": 1,
      "company": "公司",
      "position": "职位",
      "location": "地点",
      "score": 85,
      "matched": ["匹配点1"],
      "unmatched": ["不匹配点1"],
      "optimization": ["优化建议1"],
      "summary": "一句话总结"
    }
  ],
  "overall_summary": "综合分析"
}

排序规则：按score从高到低排序"""

# ============================================================
# 页面路由
# ============================================================
@app.route('/')
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

# ============================================================
# API路由
# ============================================================
@app.route('/api/parse', methods=['POST'])
def api_parse():
    """解析简历和JD"""
    try:
        # 获取简历文件
        resume_file = request.files.get('resume')
        if not resume_file:
            return jsonify({
                'error': '请上传简历',
                'solution': '点击"上传简历"按钮，选择PDF或图片格式的简历文件'
            }), 400
        
        # 读取文件内容
        resume_bytes = resume_file.read()
        resume_name = resume_file.filename
        
        print(f"[DEBUG] 收到简历文件: {resume_name}, 大小: {len(resume_bytes)} bytes")
        
        # 检查文件大小
        if len(resume_bytes) > 10 * 1024 * 1024:  # 10MB
            return jsonify({
                'error': '简历文件过大',
                'solution': '请上传小于10MB的文件，或压缩图片后重试'
            }), 400
        
        # 检查文件格式
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.txt']
        file_ext = '.' + resume_name.split('.')[-1].lower() if '.' in resume_name else ''
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f'不支持的文件格式: {file_ext}',
                'solution': '请上传PDF、PNG、JPG或TXT格式的文件'
            }), 400
        
        # 创建文件对象
        class FileWrapper:
            def __init__(self, data, name):
                self._data = data
                self.name = name
            def read(self):
                return self._data
        
        resume_wrapper = FileWrapper(resume_bytes, resume_name)
        
        # 解析简历
        print(f"[DEBUG] 开始解析简历...")
        resume = do_parse_resume(resume_wrapper)
        if not resume:
            print(f"[DEBUG] 简历解析返回None")
            return jsonify({
                'error': '简历解析失败',
                'solution': '可能原因：1) 文件内容不清晰 2) 文件格式损坏 3) MinerU服务繁忙\n解决方案：1) 重新上传更清晰的图片 2) 尝试使用PDF格式 3) 稍后重试'
            }), 400
        
        print(f"[DEBUG] 简历解析成功: {resume.name}")
        
        # 获取JD
        jds = []
        jd_files = request.files.getlist('jd_files')
        jd_texts = request.form.getlist('jd_texts')
        
        print(f"[DEBUG] 收到JD文件数量: {len(jd_files)}")
        print(f"[DEBUG] 收到JD文本数量: {len(jd_texts)}")
        
        # 打印所有收到的表单数据
        print(f"[DEBUG] 所有文件: {list(request.files.keys())}")
        print(f"[DEBUG] 所有表单字段: {list(request.form.keys())}")
        
        for i, jd_file in enumerate(jd_files):
            print(f"[DEBUG] JD文件 {i}: {jd_file.filename if jd_file else 'None'}")
            if jd_file and jd_file.filename:
                jd_bytes = jd_file.read()
                print(f"[DEBUG] JD文件 {i} 大小: {len(jd_bytes)} bytes")
                jd_wrapper = FileWrapper(jd_bytes, jd_file.filename)
                jd = do_parse_jd(jd_wrapper)
                if jd:
                    jds.append({
                        'company': jd.company,
                        'position': jd.position,
                        'location': jd.location,
                        'requirements': {
                            'must_have': [{'skill': r.skill, 'importance': r.importance} for r in jd.requirements.must_have],
                            'nice_to_have': [{'skill': r.skill, 'importance': r.importance} for r in jd.requirements.nice_to_have]
                        },
                        'responsibilities': jd.responsibilities
                    })
                    print(f"[DEBUG] JD {i} 解析成功: {jd.company} - {jd.position}")
                else:
                    print(f"[DEBUG] JD {i} 解析失败")
        
        for i, jd_text in enumerate(jd_texts):
            print(f"[DEBUG] JD文本 {i}: {jd_text[:50] if jd_text else '空'}...")
            if jd_text and jd_text.strip():
                jd = do_parse_jd(text_input=jd_text)
                if jd:
                    jds.append({
                        'company': jd.company,
                        'position': jd.position,
                        'location': jd.location,
                        'requirements': {
                            'must_have': [{'skill': r.skill, 'importance': r.importance} for r in jd.requirements.must_have],
                            'nice_to_have': [{'skill': r.skill, 'importance': r.importance} for r in jd.requirements.nice_to_have]
                        },
                        'responsibilities': jd.responsibilities
                    })
                    print(f"[DEBUG] JD文本 {i} 解析成功: {jd.company} - {jd.position}")
                else:
                    print(f"[DEBUG] JD文本 {i} 解析失败")
        
        print(f"[DEBUG] 最终JD数量: {len(jds)}")
        
        if not jds:
            return jsonify({
                'error': '请至少上传一个JD（图片或文本）',
                'debug': {
                    'jd_files_count': len(jd_files),
                    'jd_texts_count': len(jd_texts),
                    'file_keys': list(request.files.keys()),
                    'form_keys': list(request.form.keys())
                }
            }), 400
        
        resume_data = {
            'name': resume.name,
            'education': {
                'school': resume.education.school,
                'major': resume.education.major,
                'degree': resume.education.degree
            },
            'skills': resume.skills,
            'projects': [{
                'name': p.name,
                'description': p.description,
                'key_achievements': p.key_achievements,
                'technologies': p.technologies
            } for p in resume.projects]
        }
        
        return jsonify({
            'success': True,
            'resume': resume_data,
            'jds': jds
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'解析失败: {str(e)}'}), 500

@app.route('/api/match', methods=['POST'])
def api_match():
    """匹配分析 - 多Agent版本"""
    try:
        data = request.json
        resume = data.get('resume')
        jds = data.get('jds', [])
        
        if not resume or not jds:
            return jsonify({'error': '缺少简历或JD数据'}), 400
        
        print(f"[DEBUG] 开始匹配分析，JD数量: {len(jds)}")
        
        # Agent 1: 逐个JD进行匹配分析
        match_results = []
        failed_jds = []
        for i, jd in enumerate(jds):
            company = jd.get('company', '未知公司')
            position = jd.get('position', '未知职位')
            print(f"[DEBUG] 分析岗位 {i+1}/{len(jds)}: {company} - {position}")
            
            user_prompt = f"""请分析候选人与岗位的匹配度：

## 候选人简历
{json.dumps(resume, ensure_ascii=False, indent=2)}

## 目标岗位
{json.dumps(jd, ensure_ascii=False, indent=2)}

请按照要求的JSON格式输出匹配分析结果。"""

            # 重试机制
            max_retries = 2
            result = None
            for attempt in range(max_retries):
                try:
                    result = api([
                        {"role": "system", "content": MATCH_AGENT_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ], json_mode=True)
                    
                    print(f"[DEBUG] 岗位 {i+1} API返回 (尝试{attempt+1}): {type(result)}, 内容: {str(result)[:200]}")
                    
                    if result and isinstance(result, dict):
                        # 检查是否有score字段
                        score = result.get('score')
                        if score is not None:
                            # 确保score是整数
                            try:
                                score = int(score)
                            except (ValueError, TypeError):
                                score = 50
                            
                            result['company'] = company
                            result['position'] = position
                            result['location'] = jd.get('location', '')
                            result['score'] = score
                            match_results.append(result)
                            print(f"[DEBUG] 岗位 {i+1} 匹配成功，分数: {score}")
                            break  # 成功，跳出重试循环
                        else:
                            print(f"[DEBUG] 岗位 {i+1} 匹配失败: 没有score字段 (尝试{attempt+1})")
                            if attempt == max_retries - 1:
                                # 最后一次尝试，使用默认值
                                print(f"[DEBUG] 岗位 {i+1} 使用默认值")
                                result['company'] = company
                                result['position'] = position
                                result['location'] = jd.get('location', '')
                                result['score'] = 50  # 默认分数
                                result['summary'] = '匹配分析完成，但评分未能获取'
                                match_results.append(result)
                    else:
                        print(f"[DEBUG] 岗位 {i+1} 匹配失败: 返回结果为空或不是字典 (尝试{attempt+1})")
                        if attempt == max_retries - 1:
                            failed_jds.append(f"{company} - {position}")
                except Exception as e:
                    print(f"[DEBUG] 岗位 {i+1} 匹配异常 (尝试{attempt+1}): {e}")
                    if attempt == max_retries - 1:
                        failed_jds.append(f"{company} - {position}")
        
        # 返回匹配结果和失败信息
        if not match_results:
            return jsonify({
                'error': f'所有岗位匹配失败。失败岗位: {", ".join(failed_jds)}',
                'failed_jds': failed_jds
            }), 400
        
        if failed_jds:
            print(f"[WARNING] 部分岗位匹配失败: {failed_jds}")
        
        # Agent 2: 排序并生成报告
        print(f"[DEBUG] 开始生成报告")
        
        report_prompt = f"""请对以下匹配结果进行排序，生成最终报告：

{json.dumps(match_results, ensure_ascii=False, indent=2)}

请按照要求的JSON格式输出排序后的报告。"""

        report = api([
            {"role": "system", "content": REPORT_AGENT_PROMPT},
            {"role": "user", "content": report_prompt}
        ], json_mode=True)
        
        if not report:
            # 如果报告生成失败，返回原始结果
            report = {
                "ranked_results": sorted(match_results, key=lambda x: x.get('score', 0), reverse=True),
                "overall_summary": "无法生成综合报告"
            }
        
        print(f"[DEBUG] 报告生成完成")
        
        return jsonify({
            'success': True,
            'result': report
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/interview', methods=['POST'])
def api_interview():
    """生成面试准备/面试策略"""
    try:
        data = request.json
        resume = data.get('resume')
        jd = data.get('jd')
        match_result = data.get('match_result', {})
        mode = data.get('mode', 'shield')
        
        system_prompt = SHIELD_PROMPT if mode == "shield" else SPEAR_PROMPT
        
        if mode == "shield":
            # 求职者模式：需要匹配结果
            matched_raw = match_result.get('matched', [])[:3]
            missing_raw = match_result.get('unmatched', match_result.get('missing', []))[:2]
            
            matched = [m if isinstance(m, str) else m.get('requirement', '') for m in matched_raw]
            missing = [m if isinstance(m, str) else m.get('requirement', '') for m in missing_raw]
            
            user_prompt = f"""生成面试准备内容：

【简历】{json.dumps(resume, ensure_ascii=False)}
【岗位】{json.dumps(jd, ensure_ascii=False)}
【匹配】{', '.join(matched)}
【缺失】{', '.join(missing)}

要求：
1. 生成自我介绍（formal + key_points）
2. 生成3-5道面试题，每题含question、intent、answer、follow_ups

严格JSON输出：{{"self_intro":{{"formal":"","key_points":[""]}},"questions":[{{"question":"","intent":"","answer":"","follow_ups":[""]}}]}}"""
        else:
            # 面试官模式：直接根据简历和JD生成面试策略
            user_prompt = f"""请根据候选人简历和目标岗位，设计面试问题和策略：

【候选人简历】
{json.dumps(resume, ensure_ascii=False, indent=2)}

【目标岗位】
{json.dumps(jd, ensure_ascii=False, indent=2)}

要求：
1. 设计4-6个面试问题
2. 每个问题要说明为什么要问（考察什么）
3. 给出回答要点（面试官应该关注什么）
4. 说明这个问题能揭示候选人什么能力
5. 指出什么回答可能是"红旗"信号
6. 给出整体面试策略建议

严格按JSON格式输出。"""

        result = api([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], json_mode=True)
        
        if not result:
            if mode == "shield":
                result = {"self_intro": {"formal": "", "key_points": []}, "questions": []}
            else:
                result = {"questions": [], "interview_strategy": ""}
        
        if mode == "shield":
            result.setdefault("self_intro", {"formal": "", "key_points": []})
            result.setdefault("questions", [])
        else:
            result.setdefault("questions", [])
            result.setdefault("interview_strategy", "")
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mock', methods=['POST'])
def api_mock():
    """模拟面试追问"""
    try:
        data = request.json
        history = data.get('history', [])
        question = data.get('question', '')
        answer = data.get('answer', '')
        resume = data.get('resume')
        mode = data.get('mode', 'shield')
        
        system = SHIELD_PROMPT if mode == "shield" else SPEAR_PROMPT
        
        prompt = """根据回答评分、给出标准答案并追问。

JSON输出格式：
{
  "scores": {"technical_depth": 70, "quantitative_support": 80, "logical_clarity": 85},
  "overall": 78,
  "feedback": "对候选人回答的具体评价",
  "model_answer": "这个问题的标准回答，包含关键要点和最佳实践",
  "next_question": "追问问题",
  "tips": ["改进建议1", "改进建议2"]
}

要求：
1. model_answer要具体、有深度，展示最佳回答方式
2. feedback要针对候选人的具体回答进行评价
3. next_question要基于候选人的回答进行追问"""
        
        msgs = [{"role": "system", "content": system + "\n\n" + prompt}]
        for h in history[-4:]:
            msgs.append({"role": h["role"], "content": h["content"]})
        msgs.append({"role": "user", "content": f"面试题：{question}\n\n候选人回答：{answer}"})
        
        result = api(msgs, json_mode=True)
        if not result:
            result = {
                "scores": {"technical_depth": 60, "quantitative_support": 60, "logical_clarity": 60},
                "overall": 60,
                "feedback": "回答基本完整",
                "model_answer": "暂无标准答案",
                "next_question": "能详细说说吗？",
                "tips": []
            }
        
        # 确保返回的数据结构完整
        result.setdefault('scores', {"technical_depth": 60, "quantitative_support": 60, "logical_clarity": 60})
        result.setdefault('overall', 60)
        result.setdefault('feedback', '')
        result.setdefault('model_answer', '')
        result.setdefault('next_question', '')
        result.setdefault('tips', [])
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
def api_clear_cache():
    """清除缓存"""
    try:
        from cache_manager import clear_cache, get_cache_stats
        
        stats_before = get_cache_stats()
        success = clear_cache()
        stats_after = get_cache_stats()
        
        return jsonify({
            'success': success,
            'message': '缓存已清除',
            'before': stats_before,
            'after': stats_after
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/stats', methods=['GET'])
def api_cache_stats():
    """获取缓存统计"""
    try:
        from cache_manager import get_cache_stats
        stats = get_cache_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
