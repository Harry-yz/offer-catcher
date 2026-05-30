# tests/test_ui_enhanced.py
import pytest
from ui import render_progress_bar, render_skill_tags, render_score_card

def test_render_progress_bar():
    # 测试进度条渲染
    html = render_progress_bar(85, 100)
    assert "85%" in html
    assert "width: 85%" in html

def test_render_skill_tags():
    # 测试技能标签渲染
    skills = ["Python", "Java", "SQL"]
    html = render_skill_tags(skills)
    assert "Python" in html
    assert "tag" in html.lower()

def test_render_score_card():
    # 测试分数卡片渲染
    html = render_score_card(85, "高度匹配")
    assert "85" in html
    assert "高度匹配" in html
