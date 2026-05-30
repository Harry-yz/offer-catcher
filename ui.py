# ui.py
"""
Offer Catcher - 界面组件层
Streamlit UI组件封装
"""

import streamlit as st
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from models import Resume, JobDescription, MatchResult, InterviewPrep
from database import Database, User, Resume as DBResume, MatchResult as DBMatchResult

# 初始化数据库
db = Database()

# ============================================================
# UI 样式 - Slate Dark (参考Vercel/Linear)
# ============================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* 全局 */
* { font-family: 'Inter', -apple-system, sans-serif; }
.stApp { background: #0F1117; color: #E2E8F0; }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1100px; padding: 2rem 1rem; }

/* 文字 */
p, span, label, .stMarkdown { color: #94A3B8 !important; }
h1, h2, h3, h4, h5, h6, strong, b { color: #F1F5F9 !important; }
code { background: #1E293B !important; color: #38BDF8 !important; border-radius: 4px; padding: 2px 6px; }

/* 标题 */
.hero-title {
    font-size: 2.8rem; font-weight: 800; text-align: center;
    background: linear-gradient(135deg, #60A5FA, #A78BFA);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.hero-sub { text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 2rem; }

/* 卡片 */
.card {
    background: #1E293B; border: 1px solid #334155; border-radius: 12px;
    padding: 1.25rem; margin-bottom: 0.75rem;
}
.card:hover { border-color: #475569; }
.card-highlight { border-left: 3px solid #3B82F6; }

/* 按钮 */
.stButton > button {
    background: #3B82F6; color: white; border: none; border-radius: 8px;
    font-weight: 600; transition: all 0.15s;
}
.stButton > button:hover { background: #2563EB; }
.stButton > button[kind="secondary"], .stButton > button:has(span:contains("返回")) {
    background: #334155; color: #E2E8F0; border: 1px solid #475569;
}

/* 输入框 */
[data-baseweb="input"], [data-baseweb="textarea"] {
    background: #1E293B !important; border-color: #334155 !important;
}
input, textarea { color: #F1F5F9 !important; background: transparent !important; }

/* 文件上传 */
[data-testid="stFileUploader"] { background: #1E293B; border: 1px dashed #334155; border-radius: 12px; }
[data-testid="stFileUploader"] section { background: transparent; }

/* Expander */
[data-testid="stExpander"] { background: #1E293B; border: 1px solid #334155; border-radius: 10px; }
[data-testid="stExpander"] summary { color: #E2E8F0; }

/* Status */
[data-testid="stStatusWidget"] { background: #1E293B; border: 1px solid #334155; }

/* Tabs */
[data-baseweb="tab-list"] { background: #1E293B; border-radius: 10px; padding: 4px; }
[data-baseweb="tab"] { color: #64748B; border-radius: 8px; }
[data-baseweb="tab"][aria-selected="true"] { color: #F1F5F9; background: #334155; }

/* 标签 */
.tag-match { background: #064E3B; color: #6EE7B7; padding: 2px 10px; border-radius: 6px; font-size: 0.85rem; margin: 2px; display: inline-block; }
.tag-miss { background: #7F1D1D; color: #FCA5A5; padding: 2px 10px; border-radius: 6px; font-size: 0.85rem; margin: 2px; display: inline-block; }

/* 分数 */
.score-big { font-size: 2.5rem; font-weight: 800; }
.score-bar { background: #334155; border-radius: 6px; height: 8px; overflow: hidden; }
.score-fill { height: 100%; border-radius: 6px; }

/* 聊天 */
.msg-ai { background: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; }
.msg-user { background: #1E293B; border: 1px solid #3B82F6; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; margin-left: 2rem; }

/* 信息框 */
.info { background: #1E293B; border-left: 3px solid #3B82F6; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }
.success { background: #1E293B; border-left: 3px solid #10B981; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }
.warn { background: #1E293B; border-left: 3px solid #F59E0B; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; }

/* 隐藏默认 */
#MainMenu, footer { visibility: hidden; }

/* 分隔线 */
.divider { height: 1px; background: #1E293B; margin: 1.5rem 0; }
</style>
"""

def apply_css():
    """应用CSS样式"""
    st.markdown(CSS, unsafe_allow_html=True)

def render_upload_panel(role: str):
    """左侧上传面板"""
    st.markdown("### 📄 上传简历")
    resume_file = st.file_uploader("PDF / PNG / JPG", type=["pdf", "png", "jpg", "jpeg"], key=f"resume_{role}", label_visibility="collapsed")
    if resume_file:
        st.markdown(f'<div class="success">✅ {resume_file.name}</div>', unsafe_allow_html=True)

    st.markdown("### 🎯 目标岗位")
    jd_count = st.number_input("岗位数量", 1, 5, 2, key=f"jd_count_{role}")
    jd_inputs = []
    for i in range(jd_count):
        st.markdown(f"**岗位 {i+1}**")
        c1, c2 = st.columns(2)
        with c1:
            f = st.file_uploader("JD图片", type=["png", "jpg", "jpeg"], key=f"jd_f_{role}_{i}", label_visibility="collapsed")
        with c2:
            t = st.text_area("JD文本", key=f"jd_t_{role}_{i}", height=68, placeholder="粘贴JD...")
        jd_inputs.append({"file": f, "text": t})

    return resume_file, jd_inputs

def render_parsed(resume: Resume, jds: List[JobDescription]):
    """显示解析结果"""
    st.markdown(f"""<div class="card card-highlight">
        <strong>📄 {resume.name}</strong> · {resume.education.school} · {resume.education.major}<br>
        <span style="color:#64748B">技能:</span> {', '.join(resume.skills[:8])}<br>
        <span style="color:#64748B">项目:</span> {len(resume.projects)}个
    </div>""", unsafe_allow_html=True)
    
    for i, jd in enumerate(jds):
        must = [r.skill for r in jd.requirements.must_have][:4]
        st.markdown(f"""<div class="card">
            <strong>🎯 岗位{i+1}: {jd.company} - {jd.position}</strong><br>
            <span style="color:#64748B">必须:</span> {', '.join(must)}
        </div>""", unsafe_allow_html=True)
    
    st.markdown('<div class="info">点击「🎯 岗位匹配」开始匹配分析</div>', unsafe_allow_html=True)

def render_match_results(results: List[MatchResult], mode: str):
    """显示匹配结果"""
    for i, r in enumerate(results):
        score = r.overall_score
        color = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
        label = "高度匹配" if score >= 90 else "较好匹配" if score >= 70 else "一般匹配" if score >= 50 else "匹配度低"

        st.markdown(f"""<div class="card">
            <div style="display:flex;align-items:center;gap:1rem">
                <span style="background:#3B82F6;color:white;width:28px;height:28px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:0.85rem">{i+1}</span>
                <div>
                    <strong style="color:#F1F5F9">{r.company}</strong>
                    <span style="color:#64748B;margin-left:0.5rem">{r.position} · {r.location}</span>
                </div>
                <div style="margin-left:auto;text-align:right">
                    <div class="score-big" style="color:{color}">{score}</div>
                    <div style="color:{color};font-size:0.8rem">{label}</div>
                </div>
            </div>
            <div class="score-bar" style="margin-top:0.5rem"><div class="score-fill" style="width:{score}%;background:{color}"></div></div>
        </div>""", unsafe_allow_html=True)

        if r.matched:
            tags = "".join([f'<span class="tag-match">✓ {m.requirement[:25]}</span>' for m in r.matched[:5]])
            st.markdown(f"**匹配:** {tags}", unsafe_allow_html=True)
        if r.missing:
            tags = "".join([f'<span class="tag-miss">✗ {m.requirement[:25]}</span>' for m in r.missing[:3]])
            st.markdown(f"**缺失:** {tags}", unsafe_allow_html=True)

        btn_label = "🛡️ 面试准备" if mode == "shield" else "⚔️ 验证出题"
        if st.button(btn_label, key=f"prep_{mode}_{i}", use_container_width=True):
            st.session_state.selected_idx = i
            st.session_state.page = "prep"
            st.session_state.prep_result = None
            st.session_state.chat_history = []
            st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

def render_portal():
    """门户页面"""
    st.markdown('<div class="hero-title">Offer Catcher</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">AI求职智能匹配 · 求职者之盾 vs 面试官之矛</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""<div class="card" style="text-align:center">
                <div style="font-size:3rem;margin-bottom:0.5rem">🛡️</div>
                <div style="font-size:1.2rem;font-weight:700;color:#F1F5F9">求职者之盾</div>
                <div style="color:#64748B;margin-top:0.5rem">上传简历+JD<br>匹配分析 · 面试准备<br>防御性答题训练</div>
            </div>""", unsafe_allow_html=True)
            if st.button("进入求职者模式", key="btn_seeker", use_container_width=True):
                st.session_state.page = "seeker"
                st.rerun()

        with col2:
            st.markdown("""<div class="card" style="text-align:center">
                <div style="font-size:3rem;margin-bottom:0.5rem">⚔️</div>
                <div style="font-size:1.2rem;font-weight:700;color:#F1F5F9">面试官之矛</div>
                <div style="color:#64748B;margin-top:0.5rem">上传简历+JD<br>匹配分析 · 验证出题<br>破绽识别训练</div>
            </div>""", unsafe_allow_html=True)
            if st.button("进入面试官模式", key="btn_interviewer", use_container_width=True):
                st.session_state.page = "interviewer"
                st.rerun()

    st.markdown("""<div class="info" style="margin-top:2rem;max-width:600px;margin-left:auto;margin-right:auto">
        <strong>使用流程</strong><br>
        1. 选择模式（求职者/面试官）<br>
        2. 上传简历PDF/图片 + 目标JD（图片/文本，支持多个）<br>
        3. 点击「解析」→ 查看解析结果<br>
        4. 点击「岗位匹配」→ 查看匹配排名<br>
        5. 点击某岗位 → 进入面试准备/验证出题
    </div>""", unsafe_allow_html=True)

def _reset():
    """重置状态"""
    st.session_state.parsed_resume = None
    st.session_state.parsed_jds = []
    st.session_state.match_results = []
    st.session_state.selected_idx = None
    st.session_state.prep_result = None
    st.session_state.chat_history = []

def run_parse(resume_file, jd_inputs):
    """执行解析"""
    from parser import do_parse_resume, do_parse_jd
    
    with st.status("🧠 解析中...", expanded=True) as s:
        st.write("📄 解析简历...")
        resume = do_parse_resume(resume_file)
        if not resume:
            s.update(label="❌ 失败", state="error")
            return False
        st.session_state.parsed_resume = resume
        st.write(f"✅ **{resume.name}** | {len(resume.skills)}项技能 | {len(resume.projects)}个项目")

        st.write("🎯 解析岗位...")
        jds = []
        for i, inp in enumerate(jd_inputs):
            jd = do_parse_jd(inp.get("file"), inp.get("text", ""))
            if jd:
                jds.append(jd)
                st.write(f"✅ 岗位{i+1}: **{jd.company} - {jd.position}**")
        if not jds:
            st.error("所有JD解析失败")
            s.update(label="❌ 失败", state="error")
            return False
        st.session_state.parsed_jds = jds
        s.update(label="✅ 解析完成", state="complete")
    return True

def run_match():
    """执行匹配"""
    from api import api
    from config import MATCH_PROMPT
    from models import MatchResult, MatchItem, MissingItem, Optimization
    
    with st.status("🧠 匹配中...", expanded=True) as s:
        results = []
        for i, jd in enumerate(st.session_state.parsed_jds):
            st.write(f"🔄 匹配岗位{i+1}...")
            
            prompt = f"""{MATCH_PROMPT}

【简历】
{json.dumps(st.session_state.parsed_resume.__dict__, ensure_ascii=False, default=str)}

【岗位】
{json.dumps(jd.__dict__, ensure_ascii=False, default=str)}"""

            result = api([
                {"role": "system", "content": MATCH_PROMPT},
                {"role": "user", "content": f"分析匹配度：\n简历：{json.dumps(st.session_state.parsed_resume.__dict__, ensure_ascii=False, default=str)}\nJD：{json.dumps(jd.__dict__, ensure_ascii=False, default=str)}"}
            ], json_mode=True)

            if not result:
                result = {"overall_score": 0, "matched": [], "missing": [], "analysis": "解析失败"}

            # 转换为数据模型
            matched = [MatchItem(**m) for m in result.get("matched", [])]
            missing = [MissingItem(**m) for m in result.get("missing", [])]
            optimization = [Optimization(**o) for o in result.get("optimization", [])]
            
            match_result = MatchResult(
                overall_score=result.get("overall_score", 0),
                matched=matched,
                missing=missing,
                analysis=result.get("analysis", ""),
                optimization=optimization,
                company=jd.company,
                position=jd.position,
                location=jd.location
            )
            results.append(match_result)
            st.write(f"✅ {match_result.company} - {match_result.position} → **{match_result.overall_score}分**")
        
        results.sort(key=lambda x: x.overall_score, reverse=True)
        st.session_state.match_results = results
        s.update(label="✅ 匹配完成", state="complete")

def init_user_session():
    """初始化用户会话"""
    if 'user' not in st.session_state:
        # 创建临时用户
        username = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        user = User(username=username, email=f"{username}@example.com")
        st.session_state.user = db.create_user(user)

def save_resume_to_db(resume_data: dict):
    """保存简历到数据库"""
    init_user_session()
    user = st.session_state.user
    
    db_resume = DBResume(
        user_id=user.id,
        name=resume_data.get('name', ''),
        content=json.dumps(resume_data, ensure_ascii=False),
        parsed_data=json.dumps(resume_data, ensure_ascii=False)
    )
    
    return db.save_resume(db_resume)

def save_match_result_to_db(resume_id: int, jd_content: str, match_result: dict):
    """保存匹配结果到数据库"""
    init_user_session()
    user = st.session_state.user
    
    db_result = DBMatchResult(
        user_id=user.id,
        resume_id=resume_id,
        jd_content=jd_content,
        match_score=match_result.get('overall_score', 0),
        match_details=json.dumps(match_result, ensure_ascii=False)
    )
    
    return db.save_match_result(db_result)

def generate_follow_up_questions(question: str, answer: str) -> List[str]:
    """根据回答生成追问"""
    follow_ups = []
    
    # 检查是否有量化数据
    numbers = re.findall(r'\d+\.?\d*%?', answer)
    if numbers:
        follow_ups.append(f"你提到了{numbers[0]}，能详细说明是如何达到这个成果的吗？")
    
    # 检查是否提到技术栈
    tech_keywords = ['Python', 'Java', 'React', 'Django', 'SQL', 'Redis']
    for tech in tech_keywords:
        if tech.lower() in answer.lower():
            follow_ups.append(f"能详细说说你在{tech}方面的经验吗？")
    
    # 检查是否提到团队合作
    if '团队' in answer or '合作' in answer:
        follow_ups.append("在团队协作中，你遇到过什么挑战？是如何解决的？")
    
    # 默认追问
    if not follow_ups:
        follow_ups.append("能再详细描述一下这个过程吗？")
    
    return follow_ups[:3]  # 最多返回3个追问

def evaluate_answer_quality(answer: str) -> int:
    """评估回答质量"""
    score = 60  # 基础分
    
    # 检查是否有量化数据
    numbers = re.findall(r'\d+\.?\d*%?', answer)
    if numbers:
        score += 10 * len(numbers)
    
    # 检查是否有具体技术
    tech_keywords = ['Python', 'Java', 'React', 'Django', 'SQL', 'Redis', 'Docker']
    tech_count = sum(1 for tech in tech_keywords if tech.lower() in answer.lower())
    score += tech_count * 5
    
    # 检查长度
    if len(answer) > 100:
        score += 10
    
    return min(score, 100)

def render_progress_bar(value: int, max_value: int = 100) -> str:
    """渲染进度条"""
    percentage = int((value / max_value) * 100)
    color = "#10B981" if percentage >= 80 else "#F59E0B" if percentage >= 60 else "#EF4444"
    
    return f'''
    <div style="background: #334155; border-radius: 6px; height: 8px; overflow: hidden;">
        <div style="height: 100%; border-radius: 6px; width: {percentage}%; background: {color}; transition: width 0.3s;"></div>
    </div>
    <div style="text-align: right; font-size: 0.8rem; color: {color}; margin-top: 4px;">{percentage}%</div>
    '''

def render_skill_tags(skills: List[str], max_show: int = 5) -> str:
    """渲染技能标签"""
    if not skills:
        return ""
    
    tags_html = ""
    for i, skill in enumerate(skills[:max_show]):
        tags_html += f'<span class="tag-match" style="margin: 2px;">✓ {skill}</span>'
    
    if len(skills) > max_show:
        tags_html += f'<span style="color: #64748B; font-size: 0.85rem;"> +{len(skills) - max_show} more</span>'
    
    return tags_html

def render_score_card(score: int, label: str) -> str:
    """渲染分数卡片"""
    color = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
    
    return f'''
    <div class="card" style="text-align: center; padding: 1.5rem;">
        <div class="score-big" style="color: {color}; font-size: 3rem;">{score}</div>
        <div style="color: {color}; font-size: 1rem; margin-top: 0.5rem;">{label}</div>
    </div>
    '''

def render_match_summary(match_result: dict) -> str:
    """渲染匹配摘要"""
    score = match_result.get('overall_score', 0)
    matched = match_result.get('matched', [])
    missing = match_result.get('missing', [])
    
    color = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
    label = "高度匹配" if score >= 90 else "较好匹配" if score >= 70 else "一般匹配" if score >= 50 else "匹配度低"
    
    html = f'''
    <div class="card">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="score-big" style="color: {color};">{score}</div>
            <div>
                <div style="color: {color}; font-weight: 600;">{label}</div>
                <div style="color: #64748B; font-size: 0.9rem;">匹配度评分</div>
            </div>
        </div>
        <div style="margin-top: 1rem;">
            {render_progress_bar(score)}
        </div>
    '''
    
    if matched:
        html += f'''
        <div style="margin-top: 1rem;">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">匹配技能:</div>
            {render_skill_tags([m.get('requirement', '') for m in matched])}
        </div>
        '''
    
    if missing:
        html += f'''
        <div style="margin-top: 1rem;">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">缺失技能:</div>
            {render_skill_tags([m.get('requirement', '') for m in missing], 3)}
        </div>
        '''
    
    html += '</div>'
    return html
