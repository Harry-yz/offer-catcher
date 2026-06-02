# parser.py
import json
import logging
import re
from typing import Dict, Any, Optional, List
from models import Resume, JobDescription, Education, Project, Internship, WorkExperience, Certificate, Award, Requirements, Requirement

logger = logging.getLogger(__name__)

def extract_skills_from_text(text: str) -> List[str]:
    """从文本中提取技能"""
    skill_patterns = [
        r'Python', r'Java', r'SQL', r'JavaScript', r'TypeScript',
        r'React', r'Vue', r'Angular', r'Node\.js', r'Django', r'Flask',
        r'PostgreSQL', r'MySQL', r'Redis', r'MongoDB', r'Docker',
        r'Kubernetes', r'AWS', r'Azure', r'Git', r'Linux',
        r'机器学习', r'深度学习', r'自然语言处理', r'计算机视觉',
        r'LangChain', r'LLM', r'Agent', r'RAG', r'FastAPI'
    ]
    
    skills = []
    for pattern in skill_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            skills.append(pattern.replace(r'\.', '.'))
    
    return list(set(skills))

def extract_achievements(text: str) -> List[str]:
    """从文本中提取量化成就"""
    patterns = [
        r'(\d+\.?\d*%)',
        r'(\d+\.?\d*倍)',
        r'提升(\d+\.?\d*%?)',
        r'降低(\d+\.?\d*%?)',
        r'减少(\d+\.?\d*%?)',
        r'增加(\d+\.?\d*%?)',
        r'节省(\d+\.?\d*万?元)',
        r'创造(\d+\.?\d*万?元)'
    ]
    
    achievements = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            achievements.append(match)
    
    return achievements

def parse_resume_from_dict(data: Dict[str, Any], filename: str = "") -> Resume:
    """从字典解析简历数据"""
    if not data:
        return None
    
    # 如果没有name字段，尝试从文件名提取
    name = data.get("name", "").strip()
    if not name and filename:
        # 从文件名提取姓名（去掉扩展名和常见后缀）
        name = filename.replace(".pdf", "").replace(".png", "").replace(".jpg", "").replace(".jpeg", "")
        name = name.split("-")[0].split("_")[0].strip()
    
    if not name:
        name = "未知姓名"
    
    # 解析教育背景
    edu_data = data.get("education", {})
    if isinstance(edu_data, list) and len(edu_data) > 0:
        edu_data = edu_data[0]
    elif not isinstance(edu_data, dict):
        edu_data = {}
    
    education = Education(
        school=edu_data.get("school", ""),
        major=edu_data.get("major", ""),
        degree=edu_data.get("degree", ""),
        gpa=edu_data.get("gpa", ""),
        start_date=edu_data.get("start_date", ""),
        end_date=edu_data.get("end_date", "")
    )
    
    # 解析工作经历
    work_experience = []
    for work_data in data.get("work_experience", []):
        work_text = work_data.get("description", "")
        achievements = work_data.get("key_achievements", [])
        if not achievements:
            achievements = extract_achievements(work_text)
        
        work = WorkExperience(
            company=work_data.get("company", ""),
            position=work_data.get("position", ""),
            duration=work_data.get("duration", ""),
            description=work_text,
            key_achievements=achievements
        )
        work_experience.append(work)
    
    # 解析项目经历
    projects = []
    for proj_data in data.get("projects", []):
        # 从项目描述中提取技能
        project_text = proj_data.get("description", "")
        project_skills = extract_skills_from_text(project_text)
        
        # 从项目描述中提取成就
        achievements = proj_data.get("key_achievements", [])
        if not achievements:
            achievements = extract_achievements(project_text)
        
        # 合并技术栈
        technologies = proj_data.get("technologies", [])
        technologies.extend(project_skills)
        technologies = list(set(technologies))
        
        project = Project(
            name=proj_data.get("name", ""),
            description=project_text,
            key_achievements=achievements,
            technologies=technologies
        )
        projects.append(project)
    
    # 解析实习经历
    internships = []
    for intern_data in data.get("internships", []):
        intern_text = intern_data.get("description", "")
        achievements = intern_data.get("key_achievements", [])
        if not achievements:
            achievements = extract_achievements(intern_text)
        
        internship = Internship(
            company=intern_data.get("company", ""),
            position=intern_data.get("position", ""),
            duration=intern_data.get("duration", ""),
            description=intern_text,
            key_achievements=achievements
        )
        internships.append(internship)
    
    # 解析技能
    skills = data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",")]
    
    # 从所有文本中提取额外技能
    all_text = " ".join([p.get("description", "") for p in data.get("projects", [])])
    all_text += " ".join([i.get("description", "") for i in data.get("internships", [])])
    all_text += " ".join([w.get("description", "") for w in data.get("work_experience", [])])
    extra_skills = extract_skills_from_text(all_text)
    skills.extend(extra_skills)
    skills = list(set(skills))
    
    # 解析证书
    certificates = []
    for cert_data in data.get("certificates", []):
        cert = Certificate(
            name=cert_data.get("name", ""),
            issuer=cert_data.get("issuer", ""),
            date=cert_data.get("date", "")
        )
        certificates.append(cert)
    
    # 解析奖项
    awards = []
    for award_data in data.get("awards", []):
        award = Award(
            name=award_data.get("name", ""),
            date=award_data.get("date", ""),
            description=award_data.get("description", "")
        )
        awards.append(award)
    
    return Resume(
        name=name,
        phone=data.get("phone", ""),
        email=data.get("email", ""),
        location=data.get("location", ""),
        education=education,
        work_experience=work_experience,
        internships=internships,
        projects=projects,
        skills=skills,
        certificates=certificates,
        awards=awards,
        self_evaluation=data.get("self_evaluation", "")
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
    """解析简历文件（带缓存）"""
    from api import parse_text, pdf_to_text
    from config import PARSE_RESUME_PROMPT
    from mineru_parser import parse_document, is_available
    from cache_manager import get_resume_cache, save_resume_cache
    
    fb = uploaded_file.read()
    name = uploaded_file.name.lower()
    
    # 检查缓存
    cached = get_resume_cache(fb)
    if cached:
        logger.info("简历解析命中缓存")
        return parse_resume_from_dict(cached, name)
    
    # 使用MinerU解析PDF和图片
    result = None
    if name.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        if is_available():
            logger.info(f"使用MinerU解析: {name}")
            text = parse_document(fb, name)
            if text and len(text) >= 30:
                result = parse_text(text, PARSE_RESUME_PROMPT)
            else:
                logger.warning("MinerU解析结果为空或太短")
        
        # MinerU不可用时，尝试PDF文本提取
        if not result and name.endswith('.pdf'):
            text = pdf_to_text(fb)
            if len(text) >= 30:
                result = parse_text(text, PARSE_RESUME_PROMPT)
        
        if not result:
            logger.error(f"无法解析文件 {name}，MinerU可用: {is_available()}")
            return None
    else:
        # 纯文本
        result = parse_text(fb.decode('utf-8', errors='ignore'), PARSE_RESUME_PROMPT)
    
    # 保存缓存
    if result:
        save_resume_cache(fb, result)
    
    return parse_resume_from_dict(result, name)

def do_parse_jd(uploaded_file=None, text_input="") -> Optional[JobDescription]:
    """解析JD（带缓存）"""
    from api import parse_text
    from config import PARSE_JD_PROMPT
    from mineru_parser import parse_document, is_available
    from cache_manager import get_jd_cache, save_jd_cache, get_jd_text_cache, save_jd_text_cache
    
    if uploaded_file:
        fb = uploaded_file.read()
        name = uploaded_file.name.lower()
        
        # 检查缓存
        cached = get_jd_cache(fb)
        if cached:
            logger.info("JD解析命中缓存")
            return parse_jd_from_dict(cached)
        
        # 使用MinerU解析图片
        if name.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            if is_available():
                logger.info(f"使用MinerU解析JD: {name}")
                text = parse_document(fb, name)
                if text and len(text) >= 10:
                    result = parse_text(text, PARSE_JD_PROMPT)
                    # 保存缓存
                    save_jd_cache(fb, result)
                    return parse_jd_from_dict(result)
                else:
                    logger.warning("MinerU解析结果为空或太短")
            
            logger.error("无法解析图片，请确保MinerU已配置")
            return None
        else:
            result = parse_text(fb.decode('utf-8', errors='ignore'), PARSE_JD_PROMPT)
            # 保存缓存
            save_jd_cache(fb, result)
    elif text_input.strip():
        # 检查文本缓存
        cached = get_jd_text_cache(text_input)
        if cached:
            logger.info("JD文本解析命中缓存")
            return parse_jd_from_dict(cached)
        
        result = parse_text(text_input, PARSE_JD_PROMPT)
        # 保存缓存
        save_jd_text_cache(text_input, result)
    else:
        return None
    
    return parse_jd_from_dict(result)

def validate_resume_data(data: Dict[str, Any]) -> bool:
    """验证简历数据"""
    return bool(data and data.get("name"))

def validate_jd_data(data: Dict[str, Any]) -> bool:
    """验证JD数据"""
    return bool(data and data.get("company"))
