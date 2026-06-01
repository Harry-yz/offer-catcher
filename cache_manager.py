# cache_manager.py
"""
缓存管理模块
使用文件缓存，相同内容不重复解析
"""

import os
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# 缓存目录
CACHE_DIR = Path(__file__).parent / "cache"
RESUME_CACHE_DIR = CACHE_DIR / "resume"
JD_CACHE_DIR = CACHE_DIR / "jd"
MATCH_CACHE_DIR = CACHE_DIR / "match"

def init_cache():
    """初始化缓存目录"""
    RESUME_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    JD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    MATCH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"缓存目录初始化完成: {CACHE_DIR}")

def get_file_hash(file_bytes: bytes) -> str:
    """计算文件内容的MD5哈希"""
    return hashlib.md5(file_bytes).hexdigest()

def get_cache_path(cache_dir: Path, cache_key: str) -> Path:
    """获取缓存文件路径"""
    return cache_dir / f"{cache_key}.json"

def load_cache(cache_dir: Path, cache_key: str) -> Optional[Dict[str, Any]]:
    """加载缓存"""
    cache_path = get_cache_path(cache_dir, cache_key)
    if cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"缓存命中: {cache_key}")
            return data
        except Exception as e:
            logger.error(f"读取缓存失败: {e}")
            # 删除损坏的缓存文件
            cache_path.unlink(missing_ok=True)
    return None

def save_cache(cache_dir: Path, cache_key: str, data: Dict[str, Any]):
    """保存缓存"""
    cache_path = get_cache_path(cache_dir, cache_key)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"缓存保存: {cache_key}")
    except Exception as e:
        logger.error(f"保存缓存失败: {e}")

def get_resume_cache(file_bytes: bytes) -> Optional[Dict[str, Any]]:
    """获取简历解析缓存"""
    cache_key = get_file_hash(file_bytes)
    return load_cache(RESUME_CACHE_DIR, cache_key)

def save_resume_cache(file_bytes: bytes, data: Dict[str, Any]):
    """保存简历解析缓存"""
    cache_key = get_file_hash(file_bytes)
    save_cache(RESUME_CACHE_DIR, cache_key, data)

def get_jd_cache(file_bytes: bytes) -> Optional[Dict[str, Any]]:
    """获取JD解析缓存"""
    cache_key = get_file_hash(file_bytes)
    return load_cache(JD_CACHE_DIR, cache_key)

def save_jd_cache(file_bytes: bytes, data: Dict[str, Any]):
    """保存JD解析缓存"""
    cache_key = get_file_hash(file_bytes)
    save_cache(JD_CACHE_DIR, cache_key, data)

def get_jd_text_cache(text: str) -> Optional[Dict[str, Any]]:
    """获取JD文本解析缓存"""
    cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
    return load_cache(JD_CACHE_DIR, cache_key)

def save_jd_text_cache(text: str, data: Dict[str, Any]):
    """保存JD文本解析缓存"""
    cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
    save_cache(JD_CACHE_DIR, cache_key, data)

def get_match_cache(resume_hash: str, jd_hash: str) -> Optional[Dict[str, Any]]:
    """获取匹配结果缓存"""
    cache_key = f"{resume_hash}_{jd_hash}"
    return load_cache(MATCH_CACHE_DIR, cache_key)

def save_match_cache(resume_hash: str, jd_hash: str, data: Dict[str, Any]):
    """保存匹配结果缓存"""
    cache_key = f"{resume_hash}_{jd_hash}"
    save_cache(MATCH_CACHE_DIR, cache_key, data)

def clear_cache():
    """清除所有缓存"""
    import shutil
    try:
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
            init_cache()
            logger.info("缓存已清除")
            return True
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
    return False

def get_cache_stats() -> Dict[str, int]:
    """获取缓存统计"""
    def count_files(directory: Path) -> int:
        if not directory.exists():
            return 0
        return len(list(directory.glob("*.json")))
    
    return {
        "resume_count": count_files(RESUME_CACHE_DIR),
        "jd_count": count_files(JD_CACHE_DIR),
        "match_count": count_files(MATCH_CACHE_DIR)
    }

# 初始化缓存目录
init_cache()
