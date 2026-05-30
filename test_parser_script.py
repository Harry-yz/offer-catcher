import sys
sys.path.insert(0, '.')
from parser import parse_resume_from_dict, parse_jd_from_dict, validate_resume_data, validate_jd_data

def test_parse_resume_from_dict():
    data = {
        "name": "张三",
        "education": {"school": "清华大学", "major": "计算机科学", "degree": "本科"},
        "skills": ["Python", "Java"],
        "projects": [{"name": "项目1", "description": "描述", "key_achievements": ["成果1"], "technologies": ["技术1"]}]
    }
    resume = parse_resume_from_dict(data)
    assert resume is not None
    assert resume.name == "张三"
    assert resume.education.school == "清华大学"
    assert len(resume.skills) == 2
    assert len(resume.projects) == 1
    print('test_parse_resume_from_dict 通过')

def test_parse_resume_from_dict_empty():
    data = {}
    resume = parse_resume_from_dict(data)
    assert resume is None
    print('test_parse_resume_from_dict_empty 通过')

def test_parse_resume_from_dict_no_name():
    data = {"skills": ["Python"]}
    resume = parse_resume_from_dict(data)
    assert resume is None
    print('test_parse_resume_from_dict_no_name 通过')

def test_parse_jd_from_dict():
    data = {
        "company": "字节跳动",
        "position": "后端开发",
        "location": "北京",
        "requirements": {
            "must_have": [{"skill": "Python", "importance": "高"}],
            "nice_to_have": [{"skill": "Go", "importance": "中"}]
        },
        "responsibilities": ["开发后端服务"]
    }
    jd = parse_jd_from_dict(data)
    assert jd is not None
    assert jd.company == "字节跳动"
    assert len(jd.requirements.must_have) == 1
    assert len(jd.requirements.nice_to_have) == 1
    print('test_parse_jd_from_dict 通过')

def test_validate_resume_data():
    assert validate_resume_data({"name": "张三"}) == True
    assert validate_resume_data({}) == False
    assert validate_resume_data(None) == False
    print('test_validate_resume_data 通过')

def test_validate_jd_data():
    assert validate_jd_data({"company": "字节跳动"}) == True
    assert validate_jd_data({}) == False
    assert validate_jd_data(None) == False
    print('test_validate_jd_data 通过')

test_parse_resume_from_dict()
test_parse_resume_from_dict_empty()
test_parse_resume_from_dict_no_name()
test_parse_jd_from_dict()
test_validate_resume_data()
test_validate_jd_data()
print('所有解析器测试通过')
