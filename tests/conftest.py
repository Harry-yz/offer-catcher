# tests/conftest.py
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def sample_resume_data():
    """示例简历数据"""
    return {
        "name": "张三",
        "education": {"school": "清华大学", "major": "计算机科学", "degree": "本科"},
        "skills": ["Python", "Java", "SQL"],
        "projects": [
            {
                "name": "电商系统",
                "description": "负责后端开发",
                "key_achievements": ["性能提升50%"],
                "technologies": ["Python", "Django", "MySQL"]
            }
        ]
    }

@pytest.fixture
def sample_jd_data():
    """示例JD数据"""
    return {
        "company": "字节跳动",
        "position": "后端开发",
        "location": "北京",
        "requirements": {
            "must_have": [{"skill": "Python", "importance": "高"}],
            "nice_to_have": [{"skill": "Go", "importance": "中"}]
        },
        "responsibilities": ["开发后端服务"]
    }
