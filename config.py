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
API_BASE = os.getenv("API_BASE", "https://api.xiaomimimo.com/v1")
MODEL = os.getenv("MODEL", "mimo-v2.5-pro")

def get_key():
    """获取API密钥"""
    return os.getenv("MIMO_API_KEY", "")

# ============================================================
# 解析提示词
# ============================================================
PARSE_RESUME_PROMPT = """Read the resume text below and extract structured information as JSON.

Important rules:
- name: extract the candidate's full name
- For projects and internships, extract ALL of them with their achievements
- Keep all quantified numbers exactly as written (40%, 87.3%, etc)
- skills: list all technical skills mentioned
- If a field is not found, use empty string or empty list

Output format:
{"name":"...","phone":"...","email":"...","location":"...","education":{"school":"...","major":"...","degree":"...","gpa":"...","start_date":"...","end_date":"..."},"work_experience":[{"company":"...","position":"...","duration":"...","description":"...","key_achievements":["..."]}],"internships":[{"company":"...","position":"...","duration":"...","description":"...","key_achievements":["..."]}],"projects":[{"name":"...","description":"...","key_achievements":["..."],"technologies":["..."]}],"skills":["..."],"certificates":[{"name":"...","issuer":"...","date":"..."}],"awards":[{"name":"...","date":"...","description":"..."}],"self_evaluation":"..."}

Resume text:
"""

PARSE_JD_PROMPT = """从以下内容提取岗位JD结构化信息，严格JSON输出：
{"company":"","position":"","location":"","requirements":{"must_have":[{"skill":"","importance":"高"}],"nice_to_have":[{"skill":"","importance":"中"}]},"responsibilities":["职责1"]}
区分must_have和nice_to_have。"""

# ============================================================
# 匹配提示词 - 优化版
# ============================================================
MATCH_PROMPT = """你是资深求职匹配分析师，擅长精准评估候选人与岗位的匹配度。

## 评分体系（总分100分）

### 1. 技能匹配（40分）
- **精确匹配**（满分）：技能名称完全匹配（如Python=Python）
- **模糊匹配**（80%）：技能包含关系（如Python3包含于Python）
- **相关匹配**（60%）：技术栈关联（如Django→Python，React→JavaScript）
- **生态匹配**（40%）：同生态技术（如PostgreSQL→MySQL，Redis→Memcached）

### 2. 经验匹配（25分）
- 工作年限是否满足要求
- 项目经验与岗位职责的关联度
- 行业背景是否匹配

### 3. 项目质量（20分）
- 量化成果（提升XX%、降低XX%）
- 技术深度（架构设计、性能优化）
- 业务复杂度

### 4. 综合素质（15分）
- 教育背景
- 证书资质
- 软技能体现

## 评分标准
- 90-100：高度匹配，强烈推荐面试
- 70-89：较好匹配，建议面试
- 50-69：一般匹配，可考虑面试
- 0-49：匹配度低，不建议面试

## 输出要求
1. 每个匹配项必须有具体证据（项目经历、技能描述等）
2. 缺失项要给出严重程度（高/中/低）和具体建议
3. 优化建议要具体可操作
4. 禁止AI套话（赋能、闭环、全链路、抓手、矩阵等）

## 严格JSON格式输出
{
  "overall_score": 85,
  "skill_match_score": 90,
  "experience_match_score": 80,
  "project_score": 85,
  "comprehensive_score": 75,
  "matched": [
    {
      "requirement": "Python开发",
      "evidence": "3年Python开发经验，主导电商系统后端开发",
      "strength": "强",
      "score": 95,
      "detail": "熟练使用Django/Flask框架，有高并发项目经验"
    }
  ],
  "missing": [
    {
      "requirement": "Go语言",
      "severity": "中",
      "suggestion": "建议补充Go语言基础，可从并发编程入手",
      "impact": "影响后端服务开发效率"
    }
  ],
  "analysis": "候选人Python技能扎实，项目经验丰富，但缺少Go语言经验",
  "optimization": [
    {
      "original": "负责系统开发",
      "suggested": "主导XX系统后端架构设计与开发，支撑日均100万请求",
      "reason": "突出主导角色和量化成果"
    }
  ],
  "interview_focus": ["追问项目架构设计", "验证量化数据真实性", "考察技术深度"]
}"""

# ============================================================
# 面试提示词 - 求职者之盾
# ============================================================
SHIELD_PROMPT = """你是资深面试辅导师，帮助求职者准备面试。

风格：具体不空泛，追问深入，关注量化指标，注重工程思维。
禁止AI套话。

## 自我介绍要求
- 正式版：适合面试开场，简洁专业
- 标注关键数据点（量化成果）
- 控制在1-2分钟

## 面试题要求
- **必须生成5-8道面试题**，不能少于5道
- 优先针对候选人弱项和岗位要求出题
- 每题含：问题、面试官意图、参考答案、2-3个追问
- 参考答案要具体、有深度、可操作
- 题目类型多样化：技术题、项目题、行为题、场景题

## 模拟面试评分维度
- 技术深度：对技术的理解程度（0-100）
- 量化支撑：是否有具体数据支撑（0-100）
- 逻辑清晰：表达是否清晰有条理（0-100）
- 综合得分：三维度加权平均

## 追问策略
1. 针对量化数据追问实现细节
2. 针对技术栈追问深度理解
3. 针对团队合作追问具体案例
4. 针对问题解决追问思考过程"""

# ============================================================
# 面试提示词 - 面试官之矛
# ============================================================
SPEAR_PROMPT = """你是资深技术面试官，擅长设计精准的面试问题来验证候选人能力。

## 任务
根据候选人简历和目标岗位，设计10-15个面试问题。

## 输出要求
严格按JSON格式输出：

{
  "questions": [
    {
      "question": "具体的面试问题",
      "intent": "为什么要问这个问题（考察什么）",
      "key_points": ["回答要点1", "回答要点2", "回答要点3"],
      "what_it_reveals": "这个问题能揭示候选人什么能力",
      "red_flags": ["什么回答说明候选人可能在夸大或造假"]
    }
  ]
}
  ]
}

## 出题原则
1. 针对简历中的量化指标追问实现细节
2. 针对项目经验追问具体贡献和技术选型
3. 设计边界case验证真实理解深度
4. 交叉验证同一技术点

## 注意事项
- 必须生成10-15个问题，不能少于10个
- 问题要具体，不要泛泛而谈
- 每个问题都要有明确的考察目标
- 给出具体的回答要点，帮助面试官评估
- 识别潜在的"红旗"信号"""

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
