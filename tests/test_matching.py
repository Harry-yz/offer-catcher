# tests/test_matching.py
import pytest
from api import calculate_skill_match, calculate_experience_match

def test_calculate_skill_match():
    resume_skills = ["Python", "Java", "SQL"]
    jd_skills = ["Python", "Go", "SQL"]
    score = calculate_skill_match(resume_skills, jd_skills)
    assert score > 0
    assert score <= 100

def test_calculate_experience_match():
    resume_text = "3年Python开发经验"
    jd_text = "要求3年以上Python经验"
    score = calculate_experience_match(resume_text, jd_text)
    assert score > 0
