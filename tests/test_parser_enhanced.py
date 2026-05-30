# tests/test_parser_enhanced.py
import pytest
from parser import parse_resume_from_dict, extract_skills_from_text, extract_achievements

def test_extract_skills_from_text():
    text = "熟练掌握Python、Java和SQL数据库"
    skills = extract_skills_from_text(text)
    assert "Python" in skills
    assert "Java" in skills
    assert "SQL" in skills

def test_extract_achievements():
    text = "性能提升50%，成本降低40%"
    achievements = extract_achievements(text)
    assert len(achievements) >= 2
    assert "50%" in achievements[0]
    assert "40%" in achievements[1]

def test_parse_resume_with_skills_extraction():
    data = {
        "name": "张三",
        "education": {"school": "清华大学", "major": "计算机科学", "degree": "本科"},
        "skills": [],
        "projects": [{
            "name": "电商系统",
            "description": "使用Python和Django开发，性能提升50%",
            "key_achievements": [],
            "technologies": []
        }]
    }
    resume = parse_resume_from_dict(data)
    assert resume is not None
    assert "Python" in resume.skills
    assert "Django" in resume.skills
    assert len(resume.projects[0].key_achievements) > 0
