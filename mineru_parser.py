# mineru_parser.py
"""
MinerU文档解析模块
使用MinerU API解析PDF和图片
"""

import os
import logging
import requests
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)

logger = logging.getLogger(__name__)

# 创建全局Session（带重试机制）
def create_robust_session():
    """创建健壮的HTTP Session"""
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    # 配置Adapter
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    
    return session

# 全局Session实例
http_session = create_robust_session()

# MinerU配置
MINERU_API_KEY = os.getenv("MINERU_API_KEY", "")

class MineruParser:
    """MinerU文档解析器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or MINERU_API_KEY
        self.base_url = "https://mineru.net/api/v4"
        self.agent_url = "https://mineru.net/api/v1/agent"
    
    def parse_file(self, file_bytes: bytes, file_name: str) -> Optional[str]:
        """解析文件（PDF或图片）"""
        if not self.api_key:
            logger.error("MinerU API Key未配置")
            return None
        
        try:
            # 使用批量上传接口上传文件
            task_id = self._upload_and_create_task(file_bytes, file_name)
            if not task_id:
                return None
            
            # 等待任务完成并获取结果
            result = self._wait_for_result(task_id)
            return result
            
        except Exception as e:
            logger.error(f"文件解析失败: {e}")
            return None
    
    def _upload_and_create_task(self, file_bytes: bytes, file_name: str) -> Optional[str]:
        """上传文件并创建解析任务"""
        try:
            # 使用批量上传接口
            url = f"{self.base_url}/file-urls/batch"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "files": [{"name": file_name}],
                "model_version": "vlm"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0 and result.get("data"):
                batch_id = result["data"]["batch_id"]
                file_urls = result["data"]["file_urls"]
                
                if file_urls:
                    # 上传文件到OSS
                    file_url = file_urls[0]
                    put_response = requests.put(file_url, data=file_bytes, timeout=60)
                    put_response.raise_for_status()
                    
                    logger.info(f"文件上传成功，batch_id: {batch_id}")
                    return batch_id
            else:
                logger.error(f"获取上传URL失败: {result}")
                return None
                
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return None
    
    def _wait_for_result(self, batch_id: str, max_wait: int = 120) -> Optional[str]:
        """等待任务完成并获取结果"""
        url = f"{self.base_url}/extract-results/batch/{batch_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        start_time = time.time()
        poll_count = 0
        while time.time() - start_time < max_wait:
            poll_count += 1
            elapsed = int(time.time() - start_time)
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                if result.get("code") == 0 and result.get("data"):
                    data = result["data"]
                    extract_results = data.get("extract_result", [])
                    
                    if extract_results:
                        extract_result = extract_results[0]
                        state = extract_result.get("state")
                        
                        if state == "done":
                            logger.info(f"MinerU解析完成，耗时{elapsed}秒")
                            return self._download_result(extract_result)
                        elif state == "failed":
                            logger.error(f"MinerU任务失败: {extract_result}")
                            return None
                        else:
                            logger.info(f"MinerU轮询第{poll_count}次，状态: {state}，已等待{elapsed}秒")
                            time.sleep(3)
                    else:
                        logger.info(f"MinerU轮询第{poll_count}次，等待结果，已等待{elapsed}秒")
                        time.sleep(3)
                else:
                    logger.error(f"MinerU查询失败: {result}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"MinerU轮询超时，第{poll_count}次，已等待{elapsed}秒")
                time.sleep(3)
            except Exception as e:
                logger.error(f"MinerU轮询异常: {e}")
                time.sleep(3)
        
        logger.error(f"MinerU任务超时，已等待{max_wait}秒")
        return None
    
    def _download_result(self, extract_result: Dict[str, Any]) -> Optional[str]:
        """下载解析结果（使用健壮的Session）"""
        full_zip_url = extract_result.get("full_zip_url")
        if not full_zip_url:
            logger.error("未找到结果下载链接")
            return None
        
        import zipfile
        import io
        
        try:
            logger.info(f"开始下载结果: {full_zip_url[:80]}...")
            
            # 使用全局Session下载（带重试机制）
            response = http_session.get(full_zip_url, timeout=60)
            response.raise_for_status()
            logger.info(f"下载完成，大小: {len(response.content)} bytes")
            
            # 解析zip文件
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                logger.info(f"ZIP文件内容: {zip_file.namelist()}")
                # 查找markdown文件
                for file_name in zip_file.namelist():
                    if file_name.endswith('.md'):
                        with zip_file.open(file_name) as md_file:
                            text = md_file.read().decode('utf-8')
                            logger.info(f"提取到markdown，长度: {len(text)} 字符")
                            return text
                
                # 如果没有markdown文件，尝试查找其他文本文件
                for file_name in zip_file.namelist():
                    if file_name.endswith('.txt') or file_name.endswith('.json'):
                        with zip_file.open(file_name) as txt_file:
                            text = txt_file.read().decode('utf-8')
                            logger.info(f"提取到文本文件，长度: {len(text)} 字符")
                            return text
            
            logger.warning("未找到可读取的文本文件")
            return None
            
        except Exception as e:
            logger.error(f"下载结果失败: {e}")
            return None

# 全局实例
mineru_parser = MineruParser()

def parse_document(file_bytes: bytes, file_name: str) -> Optional[str]:
    """解析文档并返回文本"""
    return mineru_parser.parse_file(file_bytes, file_name)

def is_available() -> bool:
    """检查MinerU是否可用"""
    return bool(mineru_parser.api_key)
