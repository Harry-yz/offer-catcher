# Offer Catcher 技术规格文档

## 一、技术栈总览

### 1.1 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 主要开发语言 |
| Flask | 3.0+ | Web框架 |
| requests | 2.31+ | HTTP客户端 |
| python-dotenv | 1.0+ | 环境变量管理 |
| PyPDF2 | 3.0+ | PDF解析 |
| Pillow | 9.0+ | 图片处理 |
| pytest | 7.0+ | 单元测试 |

### 1.2 AI服务
| 服务 | 用途 | API地址 |
|------|------|---------|
| MinerU | 文档解析（PDF/图片→文本） | https://mineru.net/api/v4 |
| MiMo | AI推理（结构化分析） | https://api.xiaomimimo.com/v1 |

### 1.3 前端技术
| 技术 | 用途 |
|------|------|
| HTML5 | 页面结构 |
| CSS3 | 样式（毛玻璃效果、渐变色） |
| JavaScript | 交互逻辑 |
| Jinja2 | 模板引擎（Flask内置） |

---

## 二、项目结构

```
D:\AIHR\
├── server.py           # Flask主入口（16KB）
├── api.py              # API调用层（5KB）
├── parser.py           # 解析逻辑层（8KB）
├── config.py           # 配置管理（9KB）
├── models.py           # 数据模型（3KB）
├── mineru_parser.py    # MinerU封装（7KB）
├── cache_manager.py    # 缓存管理（4KB）
├── requirements.txt    # 依赖清单
├── .env                # 环境变量
├── .gitignore          # Git忽略规则
├── README.md           # 项目说明
├── templates/          # Flask模板
│   ├── index.html      # 首页（19KB）
│   ├── workbench.html  # 岗位匹配/候选人验证（56KB）
│   └── workbench_interview.html  # 面试准备（32KB）
├── tests/              # 单元测试
│   ├── test_api.py
│   ├── test_parser.py
│   ├── test_models.py
│   ├── test_database.py
│   └── test_matching.py
├── test_resource/      # 测试资源
│   ├── 张宇臻_简历186.pdf
│   └── jd1.jpg ~ jd6.jpg
├── cache/              # 缓存目录（自动生成）
│   ├── resume/
│   ├── jd/
│   └── match/
└── docs/               # 文档
    ├── project-report.md
    └── technical-spec.md
```

---

## 三、模块详解

### 3.1 server.py - Flask主入口

**职责：** 路由管理、API接口、请求处理

**主要路由：**
```python
GET  /                    # 首页
GET  /seeker              # 求职者模式
GET  /interview           # 面试准备模式
GET  /interviewer         # 面试官模式
POST /api/parse           # 解析简历和JD
POST /api/match           # 匹配分析
POST /api/interview       # 生成面试准备
POST /api/mock            # 模拟面试追问
POST /api/cache/clear     # 清除缓存
GET  /api/cache/stats     # 缓存统计
```

**关键实现：**
- 多Agent匹配架构
- 错误处理和友好提示
- 文件大小和格式验证

### 3.2 api.py - API调用层

**职责：** 封装MiMo API调用

**主要函数：**
```python
def api(messages, model=None, json_mode=False)
    # 调用MiMo API，返回文本或JSON

def extract_json(text)
    # 从文本中稳健提取JSON

def parse_text(text, prompt)
    # 文本调用API解析

def parse_image(file_bytes, prompt)
    # 图片调用API解析

def pdf_to_text(file_bytes)
    # PDF提取文本
```

**API配置：**
```python
API_BASE = "https://api.xiaomimimo.com/v1"
MODEL = "mimo-v2.5-pro"
# 认证方式：api-key头
headers = {"api-key": API_KEY}
```

### 3.3 parser.py - 解析逻辑层

**职责：** 简历和JD解析

**主要函数：**
```python
def do_parse_resume(uploaded_file)
    # 解析简历（带缓存）
    # 1. 检查缓存
    # 2. 调用MinerU提取文本
    # 3. 调用MiMo结构化解析
    # 4. 保存缓存

def do_parse_jd(uploaded_file, text_input)
    # 解析JD（带缓存）

def parse_resume_from_dict(data)
    # 从字典解析简历数据

def parse_jd_from_dict(data)
    # 从字典解析JD数据

def extract_skills_from_text(text)
    # 从文本提取技能

def extract_achievements(text)
    # 从文本提取量化成就
```

### 3.4 config.py - 配置管理

**职责：** API配置、提示词管理、环境变量

**配置项：**
```python
API_BASE = "https://api.xiaomimimo.com/v1"
MODEL = "mimo-v2.5-pro"

# 提示词
PARSE_RESUME_PROMPT  # 简历解析提示词
PARSE_JD_PROMPT      # JD解析提示词
MATCH_PROMPT         # 匹配分析提示词
SHIELD_PROMPT        # 求职者面试准备提示词
SPEAR_PROMPT         # 面试官验证提示词
```

### 3.5 models.py - 数据模型

**职责：** 定义数据结构

**主要模型：**
```python
@dataclass
class Resume:
    name: str
    education: Education
    skills: List[str]
    projects: List[Project]

@dataclass
class JobDescription:
    company: str
    position: str
    location: str
    requirements: Requirements
    responsibilities: List[str]

@dataclass
class MatchResult:
    overall_score: int
    matched: List[MatchItem]
    missing: List[MissingItem]
    optimization: List[Optimization]
```

### 3.6 mineru_parser.py - MinerU封装

**职责：** 封装MinerU API调用

**主要功能：**
```python
class MineruParser:
    def parse_file(file_bytes, file_name)
        # 1. 上传文件到MinerU
        # 2. 等待解析完成
        # 3. 下载解析结果
        # 4. 提取文本内容

    def _upload_and_create_task(file_bytes, file_name)
        # 上传文件并创建任务

    def _wait_for_result(task_id, max_wait=120)
        # 等待任务完成

    def _download_result(extract_result)
        # 下载并解析结果
```

**重试机制：**
```python
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
```

### 3.7 cache_manager.py - 缓存管理

**职责：** 文件缓存管理

**缓存策略：**
```python
# 缓存键：文件内容的MD5哈希
cache_key = hashlib.md5(file_bytes).hexdigest()

# 缓存位置
cache/resume/  # 简历缓存
cache/jd/      # JD缓存
cache/match/   # 匹配结果缓存

# 缓存操作
get_resume_cache(file_bytes)    # 获取简历缓存
save_resume_cache(file_bytes)   # 保存简历缓存
get_jd_cache(file_bytes)        # 获取JD缓存
save_jd_cache(file_bytes)       # 保存JD缓存
clear_cache()                   # 清除所有缓存
get_cache_stats()               # 缓存统计
```

---

## 四、API接口规格

### 4.1 解析接口

**请求：**
```
POST /api/parse
Content-Type: multipart/form-data

Form Fields:
- resume: File (PDF/PNG/JPG)
- jd_files: File[] (图片)
- jd_texts: string[] (文本)
```

**响应：**
```json
{
    "success": true,
    "resume": {
        "name": "张三",
        "education": {"school": "清华大学", "major": "计算机", "degree": "本科"},
        "skills": ["Python", "Java"],
        "projects": [{"name": "项目1", "description": "..."}]
    },
    "jds": [
        {
            "company": "字节跳动",
            "position": "后端开发",
            "location": "北京",
            "requirements": {
                "must_have": [{"skill": "Python", "importance": "高"}],
                "nice_to_have": [{"skill": "Go", "importance": "中"}]
            },
            "responsibilities": ["职责1"]
        }
    ]
}
```

**错误响应：**
```json
{
    "error": "简历解析失败",
    "solution": "1. 检查文件格式 2. 稍后重试"
}
```

### 4.2 匹配接口

**请求：**
```
POST /api/match
Content-Type: application/json

{
    "resume": {...},
    "jds": [{...}, {...}]
}
```

**响应：**
```json
{
    "success": true,
    "result": {
        "ranked_results": [
            {
                "rank": 1,
                "company": "腾讯",
                "position": "AI方向",
                "score": 85,
                "matched": ["Python技能匹配"],
                "unmatched": ["缺少Go经验"],
                "optimization": ["突出量化成果"],
                "summary": "技术能力匹配"
            }
        ],
        "overall_summary": "综合分析..."
    }
}
```

### 4.3 面试准备接口

**请求：**
```
POST /api/interview
Content-Type: application/json

{
    "resume": {...},
    "jd": {...},
    "match_result": {...},
    "mode": "shield"  // 或 "spear"
}
```

**响应：**
```json
{
    "success": true,
    "result": {
        "self_intro": {
            "formal": "正式版自我介绍",
            "colloquial": "口语版自我介绍",
            "key_points": ["关键数据点1", "关键数据点2"]
        },
        "questions": [
            {
                "question": "面试题",
                "intent": "考察目标",
                "answer": "参考答案",
                "colloquial_answer": "口语版答案",
                "follow_ups": ["追问1", "追问2"]
            }
        ]
    }
}
```

### 4.4 模拟面试接口

**请求：**
```
POST /api/mock
Content-Type: application/json

{
    "history": [{"role": "user", "content": "..."}],
    "question": "面试题",
    "answer": "候选人回答",
    "resume": {...},
    "mode": "shield"
}
```

**响应：**
```json
{
    "success": true,
    "result": {
        "scores": {
            "technical_depth": 70,
            "quantitative_support": 80,
            "logical_clarity": 85
        },
        "overall": 78,
        "feedback": "回答评价",
        "model_answer": "标准答案",
        "next_question": "追问",
        "tips": ["建议1", "建议2"]
    }
}
```

---

## 五、AI提示词设计

### 5.1 简历解析提示词
```
从以下内容提取简历结构化信息，严格JSON输出：
{"name":"姓名","education":{"school":"","major":"","degree":""},"skills":["技能1"],"projects":[{"name":"","description":"","key_achievements":["成果1"],"technologies":["技术1"]}]}
关键成果必须保留原始量化数据（40%、87.3%等）。
```

### 5.2 匹配分析提示词
```
你是一位资深HR顾问，擅长精准匹配候选人与岗位。

任务：分析候选人简历与目标岗位的匹配程度。

评分标准：
- 精确匹配（100%）：技能名称完全匹配
- 模糊匹配（80%）：技能包含关系
- 相关匹配（60%）：技术栈关联

输出JSON格式：
{
  "score": 75,
  "matched": ["匹配点1"],
  "unmatched": ["不匹配点1"],
  "optimization": ["优化建议1"],
  "summary": "一句话总结"
}
```

### 5.3 面试官提示词
```
你是资深技术面试官，擅长设计精准的面试问题来验证候选人能力。

任务：根据候选人简历和目标岗位，设计面试问题和策略。

输出JSON格式：
{
  "questions": [
    {
      "question": "具体的面试问题",
      "why_ask": "为什么要问这个问题",
      "key_points": ["回答要点1"],
      "what_it_reveals": "能揭示什么能力",
      "red_flags": ["红旗信号"]
    }
  ],
  "interview_strategy": "整体面试策略建议"
}
```

---

## 六、环境配置

### 6.1 环境变量
```bash
# .env文件
MIMO_API_KEY=your-mimo-api-key
MINERU_API_KEY=your-mineru-api-key
API_BASE=https://api.xiaomimimo.com/v1
MODEL=mimo-v2.5-pro
```

### 6.2 依赖安装
```bash
pip install -r requirements.txt
```

### 6.3 启动命令
```bash
python server.py
# 访问 http://localhost:8080
```

---

## 七、性能指标

| 指标 | 数值 |
|------|------|
| 简历解析时间 | 10-30秒（首次）/ 0秒（缓存） |
| JD解析时间 | 5-15秒（首次）/ 0秒（缓存） |
| 匹配分析时间 | 5-10秒 |
| 面试准备时间 | 5-10秒 |
| 缓存命中率 | 高（相同文件不重复解析） |
| 文件大小限制 | 10MB |
| 支持格式 | PDF、PNG、JPG、TXT |

---

## 八、错误处理

### 8.1 错误类型
- 文件格式错误
- 文件过大
- MinerU解析超时
- MiMo API调用失败
- 网络连接问题

### 8.2 处理策略
- 具体错误信息
- 解决方案提示
- 一键重试按钮
- 日志记录

---

## 九、安全考虑

### 9.1 API密钥
- 存储在.env文件
- 不提交到Git
- 通过环境变量加载

### 9.2 文件上传
- 格式验证
- 大小限制
- 临时文件清理

### 9.3 输入验证
- 参数类型检查
- 空值处理
- SQL注入防护（使用参数化查询）

---

**文档版本：** 1.0  
**最后更新：** 2026-05-31
