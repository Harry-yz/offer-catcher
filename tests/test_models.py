# tests/test_models.py
import pytest
from models import Resume, Education, Project, JobDescription, Requirements, Requirement

def test_resume_creation():
    resume = Resume(name="张三")
    assert resume.name == "张三"
    assert resume.skills == []
    assert resume.projects == []

def test_resume_with_education():
    edu = Education(school="清华大学", major="计算机科学", degree="本科")
    resume = Resume(name="张三", education=edu)
    assert resume.education.school == "清华大学"

def test_job_description():
    jd = JobDescription(company="字节跳动", position="后端开发")
    assert jd.company == "字节跳动"
    assert jd.requirements.must_have == []

def test_requirements():
    req = Requirement(skill="Python", importance="高")
    reqs = Requirements(must_have=[req])
    assert len(reqs.must_have) == 1
    assert reqs.must_have[0].skill == "Python"
