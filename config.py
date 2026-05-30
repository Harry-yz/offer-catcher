# config.py
"""
Offer Catcher (Offer捕手) - 配置中枢
所有提示词、Schema、Fallback数据集中管理
"""

import os
import json
import logging
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# API配置
# ============================================================
API_BASE = os.getenv("API_BASE", "https://token-plan-cn.xiaomimimo.com/v1")
MODEL = os.getenv("MODEL", "mimo-v2.5-pro")

def get_key():
    """获取API密钥"""
    # 优先从环境变量获取
    k = os.environ.get("MIMO_API_KEY", "")
    if k:
        return k
    
    # 从.env文件获取
    for p in [os.path.dirname(__file__), os.getcwd()]:
        fp = os.path.join(p, ".env")
        if os.path.exists(fp):
            try:
                with open(fp, encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("MIMO_API_KEY="):
                            v = line.strip().split("=", 1)[1].strip().strip("'\"")
                            if v and v != "your-api-key-here":
                                return v
            except Exception as e:
                logger.error(f"读取.env文件失败: {e}")
    
    # 从Streamlit secrets获取
    try:
        import streamlit as st
        v = st.secrets["MIMO_API_KEY"]
        if v and v != "your-api-key-here":
            return v
    except Exception:
        pass
    
    return ""

# ============================================================
# 解析提示词
# ============================================================
PARSE_RESUME_PROMPT = """从以下内容提取简历结构化信息，严格JSON输出：
{"name":"姓名","education":{"school":"","major":"","degree":""},"skills":["技能1"],"projects":[{"name":"","description":"","key_achievements":["成果1"],"technologies":["技术1"]}]}
关键成果必须保留原始量化数据（40%、87.3%等）。"""

PARSE_JD_PROMPT = """从以下内容提取岗位JD结构化信息，严格JSON输出：
{"company":"","position":"","location":"","requirements":{"must_have":[{"skill":"","importance":"高"}],"nice_to_have":[{"skill":"","importance":"中"}]},"responsibilities":["职责1"]}
区分must_have和nice_to_have。"""

# ============================================================
# 匹配提示词
# ============================================================
MATCH_PROMPT = """你是资深求职匹配分析师。分析简历与岗位的匹配度。

评分标准：90-100高度匹配 70-89较好 50-69一般 0-49不匹配
规则：基于证据评分，缺少必须技能该项0分，保留量化数据，禁止AI套话（赋能/闭环/全链路/抓手/矩阵）。

技能匹配计算：
- 精确匹配：技能名称完全匹配
- 模糊匹配：技能名称包含关系（如Python包含Python3）
- 相关匹配：相关技术（如Django和Python相关）

严格按此JSON格式输出：
{"overall_score":85,"matched":[{"requirement":"Python","evidence":"项目使用Python","strength":"强","score":95}],"missing":[{"requirement":"Go语言","severity":"中","suggestion":"建议补充"}],"analysis":"一句话总结","optimization":[{"original":"原表述","suggested":"建议表述","reason":"原因"}],"skill_match_score":90,"experience_match_score":85}"""

# ============================================================
# 面试提示词 - 求职者之盾
# ============================================================
SHIELD_PROMPT = """你是资深面试辅导师，帮助求职者准备面试。

风格：具体不空泛，追问深入，关注量化指标，注重工程思维。
禁止AI套话。

自我介绍：正式版+口语版（像真人说话，加语气词"嗯""其实""说实话"），标注关键数据点。
面试题：优先针对gap出题，每题含：问题、面试官意图、参考答案、口语化答案、2-3个追问。
模拟面试：按技术深度/量化支撑/逻辑清晰三维度评分(0-100)，给反馈+追问。"""

# ============================================================
# 面试提示词 - 面试官之矛
# ============================================================
SPEAR_PROMPT = """你是资深技术面试官，负责候选人验证。

目标：验证候选人项目真实性，识别简历包装。
风格：精准打击最高量化指标，追问技术细节，暴露逻辑漏洞。
禁止AI套话。

出题逻辑：
1. 精准定位候选人最强指标（如"压降40%"），追问实现细节
2. 设计边界case题，验证是否真正理解
3. 交叉验证：同一技术点从不同角度追问

每题含：验证问题、验证目标（考什么）、破绽信号（什么回答说明造假）、评分标准。"""

# ============================================================
# Fallback数据
# ============================================================
FALLBACK_RESUME = {
    "name": "张宇臻",
    "education": {"school": "香港中文大学", "major": "计算机科学", "degree": "硕士"},
    "skills": ["Python", "PostgreSQL", "Redis", "LangChain", "LLM", "Agent", "RAG", "BGE-Reranker", "FastAPI"],
    "projects": [
        {
            "name": "企业级Agent系统",
            "description": "构建高风险工作流，包含意图识别、工具调用、异常处理、HITL审核机制",
            "key_achievements": [
                "设计HITL审核机制（Accept/Reject/Edit Parameters），降低交易失败率",
                "PostgreSQL+Redis双层会话记忆，Token成本压降40%"
            ],
            "technologies": ["Python", "PostgreSQL", "Redis", "LangChain"]
        },
        {
            "name": "法律RAG系统",
            "description": "工程化'解析-检索-重排序-生成-引用'五阶段架构",
            "key_achievements": [
                "集成BGE-Reranker，Top-K检索噪声压降42%",
                "关键条款召回率从63.5%提升到87.3%"
            ],
            "technologies": ["Python", "BGE-Reranker", "RAG"]
        }
    ]
}

FALLBACK_JD = {
    "company": "字节跳动", "position": "后端开发实习生", "location": "北京",
    "requirements": {
        "must_have": [
            {"skill": "Python/Go/Java至少掌握一门", "importance": "高"},
            {"skill": "熟悉常用数据结构和算法", "importance": "高"},
            {"skill": "了解MySQL/Redis等常用存储", "importance": "高"}
        ],
        "nice_to_have": [
            {"skill": "有后端项目开发经验", "importance": "高"},
            {"skill": "了解分布式系统基础", "importance": "中"}
        ]
    },
    "responsibilities": ["参与后端服务设计与开发", "优化系统性能和稳定性"]
}
