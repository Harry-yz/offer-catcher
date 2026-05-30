# api.py
import json
import re
import base64
import requests
import logging
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class APIError(Exception):
    """API调用异常"""
    pass

def get_api_config():
    """获取API配置"""
    from config import API_BASE, MODEL, get_key
    return API_BASE, MODEL, get_key()

def api(messages: list, model: Optional[str] = None, json_mode: bool = False) -> Union[str, Dict[str, Any]]:
    """调用MiMo API，返回文本或解析后的dict"""
    api_base, default_model, key = get_api_config()
    
    if not key:
        raise APIError("未配置MIMO_API_KEY，请在.env文件或环境变量中设置")

    data = {
        "model": model or default_model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 4096
    }
    if json_mode:
        data["response_format"] = {"type": "json_object"}

    url = f"{api_base}/chat/completions"
    headers = {"Content-Type": "application/json", "api-key": key}

    logger.debug(f"API请求: {url}, 模型: {data['model']}")

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=120)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        
        if json_mode:
            return extract_json(content)
        return content
    except requests.exceptions.RequestException as e:
        logger.error(f"API请求失败: {e}")
        raise APIError(f"API请求失败: {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"API响应解析失败: {e}")
        raise APIError(f"API响应解析失败: {e}")

def extract_json(text: str) -> Dict[str, Any]:
    """从文本中稳健提取JSON - 不会崩溃"""
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 从markdown代码块提取
    m = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    
    # 从第一个{到最后一个}
    s, e = text.find('{'), text.rfind('}')
    if s != -1 and e > s:
        try:
            return json.loads(text[s:e+1])
        except json.JSONDecodeError:
            pass
    
    # 全部失败，返回空结构
    logger.warning(f"JSON提取失败，原始文本: {text[:100]}...")
    return {}

def parse_image(file_bytes: bytes, prompt: str) -> Dict[str, Any]:
    """图片转base64后调用API（用mimo-v2.5支持vision）"""
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
