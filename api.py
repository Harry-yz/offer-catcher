import json
import re
import base64
import os
import requests
import logging
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)

logger = logging.getLogger(__name__)

class APIError(Exception):
    """API调用异常"""
    pass

def api(messages: list, model: Optional[str] = None, json_mode: bool = False) -> Union[str, Dict[str, Any]]:
    """调用MiMo API，返回文本或解析后的dict"""
    
    # 【修复核心1】动态获取环境变量，防止 Gunicorn 后台运行时路径偏移导致找不到
    API_KEY = os.getenv("MIMO_API_KEY", "")
    API_BASE = os.getenv("API_BASE", "https://api.xiaomimimo.com/v1")
    
    if not API_KEY:
        raise APIError("未配置MIMO_API_KEY，请检查服务器 .env 文件！")

    data = {
        "model": model or os.getenv("MODEL", "mimo-v2.5-pro"),
        "messages": messages,
        "max_completion_tokens": 4096,
        "temperature": 0.1
    }
    
    # 【修复核心2】部分大模型强开 json_object 会报 400 错误，直接注释掉，依靠下方强大的正则提取
    # if json_mode:
    #     data["response_format"] = {"type": "json_object"}

    url = f"{API_BASE}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
        "Authorization": f"Bearer {API_KEY}" # 增加Bearer兼容不同网关设置
    }

    logger.debug(f"API请求: {url}, 模型: {data['model']}")

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=300)
        resp.raise_for_status()
        resp_json = resp.json()
        content = resp_json["choices"][0]["message"]["content"]
        
        logger.info(f"API返回内容前200字: {content[:200]}")
        
        if json_mode:
            return extract_json(content)
        return content
    except requests.exceptions.RequestException as e:
        error_msg = f"API网络请求失败: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" 详情: {e.response.text}"
        logger.error(error_msg)
        raise APIError(error_msg)
    except (KeyError, IndexError) as e:
        logger.error(f"API响应解析失败: {e}")
        raise APIError(f"API响应解析失败: {e}")

def extract_json(text: str) -> Dict[str, Any]:
    """从文本中稳健提取JSON - 绝对防崩溃"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 拆分反引号字符串
    md_block = '`' * 3
    pattern = md_block + r'(?:json)?\s*\n?([\s\S]*?)\n?' + md_block
    m = re.search(pattern, text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    
    s, e = text.find('{'), text.rfind('}')
    if s != -1 and e > s:
        try:
            return json.loads(text[s:e+1])
        except json.JSONDecodeError:
            pass
    
    logger.warning(f"JSON提取失败，原始文本前500字: {text[:500]}")
    return {}

def parse_image(file_bytes: bytes, prompt: str) -> Dict[str, Any]:
    """图片转base64后调用API"""
    b64 = base64.b64encode(file_bytes).decode()
    return api([
        {"role": "system", "content": "严格按JSON格式输出，不要添加其他文本。"},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            {"type": "text", "text": prompt}
        ]}
    ], model="mimo-v2.5", json_mode=True)

def parse_text(text: str, prompt: str) -> Dict[str, Any]:
    """文本调用API解析"""
    return api([
        {"role": "system", "content": "严格按JSON格式输出，不要添加其他文本。"},
        {"role": "user", "content": f"{prompt}\n\n{text}"}
    ], json_mode=True)

def pdf_to_text(file_bytes: bytes) -> str:
    """PDF提取文本"""
    try:
        import PyPDF2
        import io
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(p.extract_text() or "" for p in reader.pages).strip()
    except Exception as e:
        logger.error(f"PDF解析失败: {e}")
        return ""

def calculate_skill_match(resume_skills: List[str], jd_skills: List[str]) -> int:
    """计算技能匹配度"""
    if not jd_skills:
        return 100
    
    resume_skills_lower = [s.lower() for s in resume_skills]
    jd_skills_lower = [s.lower() for s in jd_skills]
    
    matched = 0
    for skill in jd_skills_lower:
        for resume_skill in resume_skills_lower:
            if skill in resume_skill or resume_skill in skill:
                matched += 1
                break
    
    return int((matched / len(jd_skills)) * 100)

def calculate_experience_match(resume_text: str, jd_text: str) -> int:
    """计算经验匹配度"""
    jd_years = re.findall(r'(\d+).*?年', jd_text)
    resume_years = re.findall(r'(\d+).*?年', resume_text)
    
    if not jd_years or not resume_years:
        return 70
    
    jd_min = int(jd_years[0])
    resume_exp = int(resume_years[0])
    
    if resume_exp >= jd_min:
        return 100
    elif resume_exp >= jd_min * 0.8:
        return 80
    else:
        return 60