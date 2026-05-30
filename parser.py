# parser.py
import json
import logging
from typing import Dict, Any, Optional
from models import Resume, JobDescription, Education, Project, Requirements, Requirement

logger = logging.getLogger(__name__)

def parse_resume_from_dict(data: Dict[str, Any]) -> Resume:
    """从字典解析简历数据"""
    if not data or not data.get("name"):
        return None
    
    # 解析教育背景
    edu_data = data.get("education", {})
    education = Education(
        school=edu_data.get("school", ""),
        major=edu_data.get("major", ""),
        degree=edu_data.get("degree", "")
    )
    
    # 解析项目经历
    projects = []
    for proj_data in data.get("projects", []):
        project = Project(
            name=proj_data.get("name", ""),
            description=proj_data.get("description", ""),
            key_achievements=proj_data.get("key_achievements", []),
            technologies=proj_data.get("technologies", [])
        )
        projects.append(project)
    
    # 解析技能
    skills = data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",")]
    
    return Resume(
        name=data.get("name", ""),
        education=education,
        skills=skills,
        projects=projects
    )

def parse_jd_from_dict(data: Dict[str, Any]) -> JobDescription:
    """从字典解析JD数据"""
    if not data or not data.get("company"):
        return None
    
    # 解析要求
    req_data = data.get("requirements", {})
    must_have = [
        Requirement(skill=r.get("skill", ""), importance=r.get("importance", "高"))
        for r in req_data.get("must_have", [])
    ]
    nice_to_have = [
        Requirement(skill=r.get("skill", ""), importance=r.get("importance", "中"))
        for r in req_data.get("nice_to_have", [])
    ]
    
    requirements = Requirements(must_have=must_have, nice_to_have=nice_to_have)
    
    return JobDescription(
        company=data.get("company", ""),
        position=data.get("position", ""),
        location=data.get("location", ""),
        requirements=requirements,
        responsibilities=data.get("responsibilities", [])
    )

def do_parse_resume(uploaded_file) -> Optional[Resume]:
    """解析简历文件"""
    from api import parse_image, parse_text, pdf_to_text
    from config import PARSE_RESUME_PROMPT
    
    fb = uploaded_file.read()
    name = uploaded_file.name.lower()
    
    if name.endswith('.pdf'):
        text = pdf_to_text(fb)
        if len(text) < 30:
            logger.warning(f"PDF文本提取失败，文本长度: {len(text)}")
            return None
        result = parse_text(text, PARSE_RESUME_PROMPT)
    elif name.endswith(('.png', '.jpg', '.jpeg')):
        result = parse_image(fb, PARSE_RESUME_PROMPT)
    else:
        result = parse_text(fb.decode('utf-8', errors='ignore'), PARSE_RESUME_PROMPT)
    
    return parse_resume_from_dict(result)

def do_parse_jd(uploaded_file=None, text_input="") -> Optional[JobDescription]:
    """解析JD"""
    from api import parse_image, parse_text
    from config import PARSE_JD_PROMPT
    
    if uploaded_file:
        fb = uploaded_file.read()
        name = uploaded_file.name.lower()
        if name.endswith(('.png', '.jpg', '.jpeg')):
            result = parse_image(fb, PARSE_JD_PROMPT)
        else:
            result = parse_text(fb.decode('utf-8', errors='ignore'), PARSE_JD_PROMPT)
    elif text_input.strip():
        result = parse_text(text_input, PARSE_JD_PROMPT)
    else:
        return None
    
    return parse_jd_from_dict(result)

def validate_resume_data(data: Dict[str, Any]) -> bool:
    """验证简历数据"""
    return bool(data and data.get("name"))

def validate_jd_data(data: Dict[str, Any]) -> bool:
    """验证JD数据"""
    return bool(data and data.get("company"))
