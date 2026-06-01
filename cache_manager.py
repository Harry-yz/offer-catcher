# cache_manager.py
"""
缓存管理模块
支持文件缓存（本地）和内存缓存（Vercel等Serverless环境）
"""

import os
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# 检测是否在Serverless环境
IS_SERVERLESS = os.environ.get('VERCEL', '') == '1' or os.environ.get('AWS_LAMBDA_FUNCTION_NAME', '') != ''

# 内存缓存（用于Serverless环境）
_memory_cache: Dict[str, Any] = {}

# 缓存目录（用于本地环境）
CACHE_DIR = Path(__file__).parent / "cache"
RESUME_CACHE_DIR = CACHE_DIR / "resume"
JD_CACHE_DIR = CACHE_DIR / "jd"
MATCH_CACHE_DIR = CACHE_DIR / "match"

def init_cache():
    """初始化缓存目录（仅本地环境）"""
    if not IS_SERVERLESS:
        try:
            RESUME_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            JD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            MATCH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"缓存目录初始化完成: {CACHE_DIR}")
        except Exception as e:
            logger.warning(f"无法创建缓存目录: {e}，将使用内存缓存")

def get_file_hash(file_bytes: bytes) -> str:
    """计算文件内容的MD5哈希"""
    return hashlib.md5(file_bytes).hexdigest()

def load_cache(cache_key: str, cache_type: str = "resume") -> Optional[Dict[str, Any]]:
    """加载缓存"""
    # 内存缓存
    full_key = f"{cache_type}:{cache_key}"
    if full_key in _memory_cache:
        logger.info(f"内存缓存命中: {full_key}")
        return _memory_cache[full_key]
    
    # 文件缓存（仅本地环境）
    if not IS_SERVERLESS:
        cache_dir = {"resume": RESUME_CACHE_DIR, "jd": JD_CACHE_DIR, "match": MATCH_CACHE_DIR}.get(cache_type, RESUME_CACHE_DIR)
        cache_path = cache_dir / f"{cache_key}.json"
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"文件缓存命中: {full_key}")
                # 同时保存到内存缓存
                _memory_cache[full_key] = data
                return data
            except Exception as e:
                logger.error(f"读取缓存失败: {e}")
                cache_path.unlink(missing_ok=True)
    
    return None

def save_cache(cache_key: str, data: Dict[str, Any], cache_type: str = "resume"):
    """保存缓存"""
    full_key = f"{cache_type}:{cache_key}"
    
    # 保存到内存缓存
    _memory_cache[full_key] = data
    logger.info(f"缓存保存到内存: {full_key}")
    
    # 文件缓存（仅本地环境）
    if not IS_SERVERLESS:
        cache_dir = {"resume": RESUME_CACHE_DIR, "jd": JD_CACHE_DIR, "match": MATCH_CACHE_DIR}.get(cache_type, RESUME_CACHE_DIR)
        cache_path = cache_dir / f"{cache_key}.json"
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"缓存保存到文件: {full_key}")
        except Exception as e:
            logger.warning(f"保存缓存到文件失败: {e}")

def get_resume_cache(file_bytes: bytes) -> Optional[Dict[str, Any]]:
    """获取简历解析缓存"""
    cache_key = get_file_hash(file_bytes)
    return load_cache(cache_key, "resume")

def save_resume_cache(file_bytes: bytes, data: Dict[str, Any]):
    """保存简历解析缓存"""
    cache_key = get_file_hash(file_bytes)
    save_cache(cache_key, data, "resume")

def get_jd_cache(file_bytes: bytes) -> Optional[Dict[str, Any]]:
    """获取JD解析缓存"""
    cache_key = get_file_hash(file_bytes)
    return load_cache(cache_key, "jd")

def save_jd_cache(file_bytes: bytes, data: Dict[str, Any]):
    """保存JD解析缓存"""
    cache_key = get_file_hash(file_bytes)
    save_cache(cache_key, data, "jd")

def get_jd_text_cache(text: str) -> Optional[Dict[str, Any]]:
    """获取JD文本解析缓存"""
    cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
    return load_cache(cache_key, "jd")

def save_jd_text_cache(text: str, data: Dict[str, Any]):
    """保存JD文本解析缓存"""
    cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
    save_cache(cache_key, data, "jd")

def get_match_cache(resume_hash: str, jd_hash: str) -> Optional[Dict[str, Any]]:
    """获取匹配结果缓存"""
    cache_key = f"{resume_hash}_{jd_hash}"
    return load_cache(cache_key, "match")

def save_match_cache(resume_hash: str, jd_hash: str, data: Dict[str, Any]):
    """保存匹配结果缓存"""
    cache_key = f"{resume_hash}_{jd_hash}"
    save_cache(cache_key, data, "match")

def clear_cache():
    """清除所有缓存"""
    global _memory_cache
    _memory_cache = {}
    
    if not IS_SERVERLESS:
        import shutil
        try:
            if CACHE_DIR.exists():
                shutil.rmtree(CACHE_DIR)
                init_cache()
                logger.info("文件缓存已清除")
        except Exception as e:
            logger.error(f"清除文件缓存失败: {e}")
    
    logger.info("内存缓存已清除")
    return True

def get_cache_stats() -> Dict[str, int]:
    """获取缓存统计"""
    if IS_SERVERLESS:
        # 内存缓存统计
        resume_count = sum(1 for k in _memory_cache if k.startswith("resume:"))
        jd_count = sum(1 for k in _memory_cache if k.startswith("jd:"))
        match_count = sum(1 for k in _memory_cache if k.startswith("match:"))
        return {
            "resume_count": resume_count,
            "jd_count": jd_count,
            "match_count": match_count,
            "cache_type": "memory"
        }
    else:
        # 文件缓存统计
        def count_files(directory: Path) -> int:
            if not directory.exists():
                return 0
            return len(list(directory.glob("*.json")))
        
        return {
            "resume_count": count_files(RESUME_CACHE_DIR),
            "jd_count": count_files(JD_CACHE_DIR),
            "match_count": count_files(MATCH_CACHE_DIR),
            "cache_type": "file"
        }

# 初始化缓存目录（仅本地环境）
init_cache()
