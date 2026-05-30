# app.py
"""
Offer Catcher (Offer捕手) V3
求职者之盾 vs 面试官之矛
"""

import streamlit as st
from ui import apply_css, render_portal, render_parsed, render_match_results, _reset, run_parse, run_match

# ============================================================
# Session State
# ============================================================
def init_state():
    defaults = {
        "page": "portal",  # portal / seeker / interviewer / prep
        "parsed_resume": None,
        "parsed_jds": [],
        "match_results": [],
        "selected_idx": None,
        "prep_result": None,
        "chat_history": [],
        "q_idx": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ============================================================
# 页面: 求职者工作台
# ============================================================
def page_seeker():
    st.markdown('<div class="hero-title" style="font-size:2rem">🛡️ 求职者之盾</div>', unsafe_allow_html=True)
    if st.button("← 返回首页"):
        st.session_state.page = "portal"
        _reset()
        st.rerun()
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([2, 3])
    with col_l:
        resume_file, jd_inputs = render_upload_panel("seeker")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📄 解析", key="parse_s", use_container_width=True):
                if not resume_file:
                    st.error("请上传简历")
                else:
                    run_parse(resume_file, jd_inputs)
                    st.rerun()
        with c2:
            if st.button("🎯 岗位匹配", key="match_s", use_container_width=True):
                if not st.session_state.parsed_resume:
                    st.warning("请先解析")
                elif not st.session_state.parsed_jds:
                    st.warning("请先解析JD")
                else:
                    run_match()
                    st.rerun()

    with col_r:
        if st.session_state.match_results:
            render_match_results(st.session_state.match_results, "shield")
        elif st.session_state.parsed_resume:
            render_parsed(st.session_state.parsed_resume, st.session_state.parsed_jds)
        else:
            st.markdown("""<div style="text-align:center;padding:5rem 2rem;color:#475569">
                <div style="font-size:3rem;opacity:0.3">📊</div>
                <div>上传简历和JD后，点击「解析」</div>
            </div>""", unsafe_allow_html=True)

# ============================================================
# 页面: 面试官工作台
# ============================================================
def page_interviewer():
    st.markdown('<div class="hero-title" style="font-size:2rem">⚔️ 面试官之矛</div>', unsafe_allow_html=True)
    if st.button("← 返回首页"):
        st.session_state.page = "portal"
        _reset()
        st.rerun()
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([2, 3])
    with col_l:
        resume_file, jd_inputs = render_upload_panel("interviewer")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📄 解析", key="parse_i", use_container_width=True):
                if not resume_file:
                    st.error("请上传简历")
                else:
                    run_parse(resume_file, jd_inputs)
                    st.rerun()
        with c2:
            if st.button("🎯 岗位匹配", key="match_i", use_container_width=True):
                if not st.session_state.parsed_resume:
                    st.warning("请先解析")
                elif not st.session_state.parsed_jds:
                    st.warning("请先解析JD")
                else:
                    run_match()
                    st.rerun()

    with col_r:
        if st.session_state.match_results:
            render_match_results(st.session_state.match_results, "interviewer")
        elif st.session_state.parsed_resume:
            render_parsed(st.session_state.parsed_resume, st.session_state.parsed_jds)
        else:
            st.markdown("""<div style="text-align:center;padding:5rem 2rem;color:#475569">
                <div style="font-size:3rem;opacity:0.3">⚔️</div>
                <div>上传简历和JD后，点击「解析」</div>
            </div>""", unsafe_allow_html=True)

# ============================================================
# 页面: 面试准备 (盾) / 验证出题 (矛)
# ============================================================
def page_prep():
    idx = st.session_state.selected_idx
    if idx is None or idx >= len(st.session_state.match_results):
        st.error("未选择岗位")
        return

    r = st.session_state.match_results[idx]
    mode = "shield" if st.session_state.get("_from", "seeker") == "seeker" else "spear"

    title = "🛡️ 面试准备" if mode == "shield" else "⚔️ 验证出题"
    st.markdown(f'<div class="hero-title" style="font-size:2rem">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">{r.company} · {r.position}</div>', unsafe_allow_html=True)

    back_page = "seeker" if mode == "shield" else "interviewer"
    if st.button("← 返回匹配结果"):
        st.session_state.page = back_page
        st.rerun()
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    resume = st.session_state.parsed_resume
    jd = st.session_state.parsed_jds[idx] if idx < len(st.session_state.parsed_jds) else None

    # 生成按钮
    if not st.session_state.prep_result:
        if st.button(f"{'🛡️ 生成面试准备' if mode == 'shield' else '⚔️ 生成验证题目'}", use_container_width=True):
            with st.spinner("生成中..."):
                from ui import do_interview
                st.session_state.prep_result = do_interview(resume, jd, r, mode)
            st.rerun()
        return

    prep = st.session_state.prep_result
    intro = prep.get("self_intro", {})
    questions = prep.get("questions", [])

    tab_names = ["📝 自我介绍", "❓ 面试题库", "💬 模拟面试"]
    tabs = st.tabs(tab_names)

    # Tab 1: 自我介绍
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📄 正式版**")
            st.markdown(f'<div class="card">{intro.get("formal","")}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("**🗣️ 口语版**")
            st.markdown(f'<div class="card">{intro.get("colloquial","")}</div>', unsafe_allow_html=True)
        kp = intro.get("key_points", [])
        if kp:
            st.markdown("**🎯 关键数据点**")
            for p in kp:
                st.markdown(f'<div class="info">{p}</div>', unsafe_allow_html=True)

    # Tab 2: 题库
    with tabs[1]:
        for i, q in enumerate(questions):
            with st.expander(f"Q{i+1}: {q.get('question','')[:50]}..."):
                st.markdown(f"**问题:** {q.get('question','')}")
                st.markdown(f"**{'🛡️ 面试官意图' if mode == 'shield' else '⚔️ 验证目标'}:** {q.get('intent','')}")
                st.markdown(f"**💡 参考答案:**")
                st.write(q.get('answer',''))
                st.markdown(f"**🗣️ 口语版:**")
                st.markdown(f'<div class="card">{q.get("colloquial_answer","")}</div>', unsafe_allow_html=True)
                fus = q.get("follow_ups", [])
                if fus:
                    st.markdown("**🔄 追问链:**")
                    for j, fu in enumerate(fus):
                        st.markdown(f"  {j+1}. {fu}")

    # Tab 3: 模拟面试
    with tabs[2]:
        if not questions:
            st.warning("请先在题库Tab生成题目")
            return

        q_idx = st.session_state.q_idx
        if q_idx >= len(questions):
            q_idx = 0
        cur_q = questions[q_idx]

        st.markdown(f'<div class="info"><strong>当前问题:</strong> {cur_q.get("question","")}</div>', unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            cls = "msg-ai" if msg["role"] == "assistant" else "msg-user"
            icon = "🤖" if msg["role"] == "assistant" else "👤"
            st.markdown(f'<div class="{cls}"><strong>{icon} {"面试官" if msg["role"]=="assistant" else "你"}:</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

        user_input = st.text_area("输入你的回答:", key="mock_input", height=100, placeholder="输入回答...")
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("📤 发送", use_container_width=True):
                if user_input.strip():
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    with st.spinner("思考中..."):
                        from ui import do_mock_reply
                        resp = do_mock_reply(st.session_state.chat_history, cur_q.get("question",""), user_input, resume, mode)
                    scores = resp.get("scores", {})
                    reply = f"""**评分:** 技术深度 {scores.get('technical_depth',0)} | 量化支撑 {scores.get('quantitative_support',0)} | 逻辑清晰 {scores.get('logical_clarity',0)} | 综合 {resp.get('overall',0)}

**反馈:** {resp.get('feedback','')}

**追问:** {resp.get('next_question','')}"""
                    tips = resp.get("tips", [])
                    if tips:
                        reply += "\n\n**建议:**\n" + "\n".join([f"- {t}" for t in tips])
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    st.rerun()
        with c2:
            if st.button("⏭️ 下一题", use_container_width=True):
                st.session_state.q_idx = (q_idx + 1) % len(questions)
                st.session_state.chat_history = []
                st.rerun()

# ============================================================
# 主路由
# ============================================================
def main():
    st.set_page_config(page_title="Offer Catcher", page_icon="🎯", layout="wide", initial_sidebar_state="collapsed")
    apply_css()
    init_state()

    # 记录来源页面（用于判断盾/矛模式）
    if st.session_state.page in ("seeker", "interviewer"):
        st.session_state["_from"] = st.session_state.page

    if st.session_state.page == "portal":
        render_portal()
    elif st.session_state.page == "seeker":
        page_seeker()
    elif st.session_state.page == "interviewer":
        page_interviewer()
    elif st.session_state.page == "prep":
        page_prep()
    else:
        render_portal()

if __name__ == "__main__":
    main()
