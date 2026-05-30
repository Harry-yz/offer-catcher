# Offer Catcher 功能改进实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 提升Offer Catcher的简历解析准确性、匹配算法、面试模拟质量、数据持久化和用户界面

**Architecture:** 基于现有模块化架构，逐步改进各个功能模块

**Tech Stack:** Python 3.9+, Streamlit, Pydantic, SQLite, python-dotenv

---

## 文件结构

- **Modify:** `parser.py` - 提升简历解析准确性
- **Modify:** `api.py` - 优化匹配算法
- **Modify:** `ui.py` - 增强面试模拟质量和改进用户界面
- **Create:** `database.py` - 添加数据持久化
- **Modify:** `config.py` - 更新配置
- **Create:** `tests/test_database.py` - 数据库测试
- **Create:** `tests/test_parser_enhanced.py` - 解析器增强测试

---

## Task 1: 提升简历解析准确性

**Files:**
- Modify: `parser.py`
- Create: `tests/test_parser_enhanced.py`

- [ ] **Step 1: 创建增强的解析器测试**

```python
# tests/test_parser_enhanced.py
import pytest
from parser import parse_resume_from_dict, extract_skills_from_text, extract_achievements

def test_extract_skills_from_text():
    text = "熟练掌握Python、Java和SQL数据库"
    skills = extract_skills_from_text(text)
    assert "Python" in skills
    assert "Java" in skills
    assert "SQL" in skills

def test_extract_achievements():
    text = "性能提升50%，成本降低40%"
    achievements = extract_achievements(text)
    assert len(achievements) >= 2
    assert "50%" in achievements[0]
    assert "40%" in achievements[1]

def test_parse_resume_with_skills_extraction():
    data = {
        "name": "张三",
        "education": {"school": "清华大学", "major": "计算机科学", "degree": "本科"},
        "skills": [],
        "projects": [{
            "name": "电商系统",
            "description": "使用Python和Django开发，性能提升50%",
            "key_achievements": [],
            "technologies": []
        }]
    }
    resume = parse_resume_from_dict(data)
    assert resume is not None
    assert "Python" in resume.skills
    assert "Django" in resume.skills
    assert len(resume.projects[0].key_achievements) > 0
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_parser_enhanced.py -v`
Expected: FAIL with "extract_skills_from_text not defined"

- [ ] **Step 3: 实现技能提取功能**

```python
# parser.py 添加新函数
import re
from typing import List

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
```

- [ ] **Step 4: 更新parse_resume_from_dict函数**

```python
# parser.py 修改parse_resume_from_dict函数
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
    
    # 解析技能
    skills = data.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",")]
    
    # 从项目描述中提取额外技能
    all_project_text = " ".join([p.get("description", "") for p in data.get("projects", [])])
    extra_skills = extract_skills_from_text(all_project_text)
    skills.extend(extra_skills)
    skills = list(set(skills))
    
    return Resume(
        name=data.get("name", ""),
        education=education,
        skills=skills,
        projects=projects
    )
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_parser_enhanced.py -v`
Expected: PASS

- [ ] **Step 6: 提交更改**

```bash
git add parser.py tests/test_parser_enhanced.py
git commit -m "feat: enhance resume parsing with skill and achievement extraction"
```

---

## Task 2: 优化匹配算法

**Files:**
- Modify: `api.py`
- Modify: `config.py`

- [ ] **Step 1: 创建匹配算法测试**

```python
# tests/test_matching.py
import pytest
from api import calculate_skill_match, calculate_experience_match

def test_calculate_skill_match():
    resume_skills = ["Python", "Java", "SQL"]
    jd_skills = ["Python", "Go", "SQL"]
    score = calculate_skill_match(resume_skills, jd_skills)
    assert score > 0
    assert score <= 100

def test_calculate_experience_match():
    resume_text = "3年Python开发经验"
    jd_text = "要求3年以上Python经验"
    score = calculate_experience_match(resume_text, jd_text)
    assert score > 0
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_matching.py -v`
Expected: FAIL with "calculate_skill_match not defined"

- [ ] **Step 3: 实现匹配算法**

```python
# api.py 添加新函数
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
    import re
    
    # 提取年限要求
    jd_years = re.findall(r'(\d+).*?年', jd_text)
    resume_years = re.findall(r'(\d+).*?年', resume_text)
    
    if not jd_years or not resume_years:
        return 70  # 默认分数
    
    jd_min = int(jd_years[0])
    resume_exp = int(resume_years[0])
    
    if resume_exp >= jd_min:
        return 100
    elif resume_exp >= jd_min * 0.8:
        return 80
    else:
        return 60
```

- [ ] **Step 4: 更新匹配提示词**

```python
# config.py 更新MATCH_PROMPT
MATCH_PROMPT = """你是资深求职匹配分析师。分析简历与岗位的匹配度。

评分标准：90-100高度匹配 70-89较好 50-69一般 0-49不匹配
规则：基于证据评分，缺少必须技能该项0分，保留量化数据，禁止AI套话（赋能/闭环/全链路/抓手/矩阵）。

技能匹配计算：
- 精确匹配：技能名称完全匹配
- 模糊匹配：技能名称包含关系（如Python包含Python3）
- 相关匹配：相关技术（如Django和Python相关）

严格按此JSON格式输出：
{"overall_score":85,"matched":[{"requirement":"Python","evidence":"项目使用Python","strength":"强","score":95}],"missing":[{"requirement":"Go语言","severity":"中","suggestion":"建议补充"}],"analysis":"一句话总结","optimization":[{"original":"原表述","suggested":"建议表述","reason":"原因"}],"skill_match_score":90,"experience_match_score":85}"""
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_matching.py -v`
Expected: PASS

- [ ] **Step 6: 提交更改**

```bash
git add api.py config.py tests/test_matching.py
git commit -m "feat: optimize matching algorithm with skill and experience scoring"
```

---

## Task 3: 增强面试模拟质量

**Files:**
- Modify: `ui.py`
- Modify: `config.py`

- [ ] **Step 1: 创建面试模拟测试**

```python
# tests/test_interview.py
import pytest
from ui import generate_follow_up_questions, evaluate_answer_quality

def test_generate_follow_up_questions():
    question = "请介绍一下你最成功的项目"
    answer = "我负责开发了一个电商系统，使用Python和Django"
    follow_ups = generate_follow_up_questions(question, answer)
    assert len(follow_ups) > 0
    assert all(isinstance(q, str) for q in follow_ups)

def test_evaluate_answer_quality():
    answer = "我使用Python开发了系统，性能提升了50%，用户满意度提高了30%"
    score = evaluate_answer_quality(answer)
    assert score > 0
    assert score <= 100
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_interview.py -v`
Expected: FAIL with "generate_follow_up_questions not defined"

- [ ] **Step 3: 实现面试增强功能**

```python
# ui.py 添加新函数
def generate_follow_up_questions(question: str, answer: str) -> List[str]:
    """根据回答生成追问"""
    follow_ups = []
    
    # 检查是否有量化数据
    import re
    numbers = re.findall(r'\d+\.?\d*%?', answer)
    if numbers:
        follow_ups.append(f"你提到了{numbers[0]}，能详细说明是如何达到这个成果的吗？")
    
    # 检查是否提到技术栈
    tech_keywords = ['Python', 'Java', 'React', 'Django', 'SQL', 'Redis']
    for tech in tech_keywords:
        if tech.lower() in answer.lower():
            follow_ups.append(f"能详细说说你在{tech}方面的经验吗？")
    
    # 检查是否提到团队合作
    if '团队' in answer or '合作' in answer:
        follow_ups.append("在团队协作中，你遇到过什么挑战？是如何解决的？")
    
    # 默认追问
    if not follow_ups:
        follow_ups.append("能再详细描述一下这个过程吗？")
    
    return follow_ups[:3]  # 最多返回3个追问

def evaluate_answer_quality(answer: str) -> int:
    """评估回答质量"""
    score = 60  # 基础分
    
    # 检查是否有量化数据
    import re
    numbers = re.findall(r'\d+\.?\d*%?', answer)
    if numbers:
        score += 10 * len(numbers)
    
    # 检查是否有具体技术
    tech_keywords = ['Python', 'Java', 'React', 'Django', 'SQL', 'Redis', 'Docker']
    tech_count = sum(1 for tech in tech_keywords if tech.lower() in answer.lower())
    score += tech_count * 5
    
    # 检查长度
    if len(answer) > 100:
        score += 10
    
    return min(score, 100)
```

- [ ] **Step 4: 更新面试提示词**

```python
# config.py 更新SHIELD_PROMPT
SHIELD_PROMPT = """你是资深面试辅导师，帮助求职者准备面试。

风格：具体不空泛，追问深入，关注量化指标，注重工程思维。
禁止AI套话。

自我介绍：正式版+口语版（像真人说话，加语气词"嗯""其实""说实话"），标注关键数据点。
面试题：优先针对gap出题，每题含：问题、面试官意图、参考答案、口语化答案、2-3个追问。
模拟面试：按技术深度/量化支撑/逻辑清晰三维度评分(0-100)，给反馈+追问。

追问策略：
1. 针对量化数据追问实现细节
2. 针对技术栈追问深度理解
3. 针对团队合作追问具体案例
4. 针对问题解决追问思考过程

评分维度：
- 技术深度：对技术的理解程度（0-100）
- 量化支撑：是否有具体数据支撑（0-100）
- 逻辑清晰：表达是否清晰有条理（0-100）
- 综合得分：三维度加权平均"""
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_interview.py -v`
Expected: PASS

- [ ] **Step 6: 提交更改**

```bash
git add ui.py config.py tests/test_interview.py
git commit -m "feat: enhance interview simulation with follow-up questions and quality evaluation"
```

---

## Task 4: 添加数据持久化

**Files:**
- Create: `database.py`
- Modify: `ui.py`
- Create: `tests/test_database.py`

- [ ] **Step 1: 创建数据库测试**

```python
# tests/test_database.py
import pytest
import os
from database import Database, User, Resume, MatchResult

def test_database_creation():
    db = Database("test.db")
    assert db is not None
    os.remove("test.db")

def test_user_operations():
    db = Database("test.db")
    user = User(username="testuser", email="test@example.com")
    db.create_user(user)
    retrieved = db.get_user("testuser")
    assert retrieved is not None
    assert retrieved.username == "testuser"
    os.remove("test.db")

def test_resume_operations():
    db = Database("test.db")
    user = User(username="testuser", email="test@example.com")
    db.create_user(user)
    
    resume = Resume(user_id=user.id, name="张三", content="简历内容")
    db.save_resume(resume)
    
    resumes = db.get_user_resumes(user.id)
    assert len(resumes) == 1
    assert resumes[0].name == "张三"
    os.remove("test.db")
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_database.py -v`
Expected: FAIL with "Database not defined"

- [ ] **Step 3: 实现数据库模块**

```python
# database.py
import sqlite3
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
import json

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    created_at: str = ""

@dataclass
class Resume:
    id: Optional[int] = None
    user_id: int = 0
    name: str = ""
    content: str = ""
    parsed_data: str = ""
    created_at: str = ""

@dataclass
class MatchResult:
    id: Optional[int] = None
    user_id: int = 0
    resume_id: int = 0
    jd_content: str = ""
    match_score: int = 0
    match_details: str = ""
    created_at: str = ""

@dataclass
class InterviewSession:
    id: Optional[int] = None
    user_id: int = 0
    resume_id: int = 0
    jd_content: str = ""
    mode: str = "shield"
    questions: str = ""
    answers: str = ""
    scores: str = ""
    created_at: str = ""

class Database:
    def __init__(self, db_path: str = "offer_catcher.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                content TEXT,
                parsed_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                resume_id INTEGER,
                jd_content TEXT,
                match_score INTEGER,
                match_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                resume_id INTEGER,
                jd_content TEXT,
                mode TEXT,
                questions TEXT,
                answers TEXT,
                scores TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, user: User) -> User:
        """创建用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (user.username, user.email)
        )
        
        user.id = cursor.lastrowid
        user.created_at = datetime.now().isoformat()
        
        conn.commit()
        conn.close()
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return User(id=row[0], username=row[1], email=row[2], created_at=row[3])
        return None
    
    def save_resume(self, resume: Resume) -> Resume:
        """保存简历"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO resumes (user_id, name, content, parsed_data) VALUES (?, ?, ?, ?)",
            (resume.user_id, resume.name, resume.content, resume.parsed_data)
        )
        
        resume.id = cursor.lastrowid
        resume.created_at = datetime.now().isoformat()
        
        conn.commit()
        conn.close()
        return resume
    
    def get_user_resumes(self, user_id: int) -> List[Resume]:
        """获取用户简历"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM resumes WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        
        conn.close()
        
        return [Resume(id=row[0], user_id=row[1], name=row[2], content=row[3], parsed_data=row[4], created_at=row[5]) for row in rows]
    
    def save_match_result(self, result: MatchResult) -> MatchResult:
        """保存匹配结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO match_results (user_id, resume_id, jd_content, match_score, match_details) VALUES (?, ?, ?, ?, ?)",
            (result.user_id, result.resume_id, result.jd_content, result.match_score, result.match_details)
        )
        
        result.id = cursor.lastrowid
        result.created_at = datetime.now().isoformat()
        
        conn.commit()
        conn.close()
        return result
    
    def save_interview_session(self, session: InterviewSession) -> InterviewSession:
        """保存面试会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO interview_sessions (user_id, resume_id, jd_content, mode, questions, answers, scores) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session.user_id, session.resume_id, session.jd_content, session.mode, session.questions, session.answers, session.scores)
        )
        
        session.id = cursor.lastrowid
        session.created_at = datetime.now().isoformat()
        
        conn.commit()
        conn.close()
        return session
```

- [ ] **Step 4: 更新UI集成数据库**

```python
# ui.py 添加数据库集成
from database import Database, User, Resume as DBResume, MatchResult as DBMatchResult

# 初始化数据库
db = Database()

def init_user_session():
    """初始化用户会话"""
    if 'user' not in st.session_state:
        # 创建临时用户
        username = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        user = User(username=username, email=f"{username}@example.com")
        st.session_state.user = db.create_user(user)

def save_resume_to_db(resume_data: dict):
    """保存简历到数据库"""
    init_user_session()
    user = st.session_state.user
    
    db_resume = DBResume(
        user_id=user.id,
        name=resume_data.get('name', ''),
        content=json.dumps(resume_data, ensure_ascii=False),
        parsed_data=json.dumps(resume_data, ensure_ascii=False)
    )
    
    return db.save_resume(db_resume)

def save_match_result_to_db(resume_id: int, jd_content: str, match_result: dict):
    """保存匹配结果到数据库"""
    init_user_session()
    user = st.session_state.user
    
    db_result = DBMatchResult(
        user_id=user.id,
        resume_id=resume_id,
        jd_content=jd_content,
        match_score=match_result.get('overall_score', 0),
        match_details=json.dumps(match_result, ensure_ascii=False)
    )
    
    return db.save_match_result(db_result)
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_database.py -v`
Expected: PASS

- [ ] **Step 6: 提交更改**

```bash
git add database.py ui.py tests/test_database.py
git commit -m "feat: add data persistence with SQLite database"
```

---

## Task 5: 改进用户界面

**Files:**
- Modify: `ui.py`
- Modify: `app.py`

- [ ] **Step 1: 创建UI测试**

```python
# tests/test_ui_enhanced.py
import pytest
from ui import render_progress_bar, render_skill_tags, render_score_card

def test_render_progress_bar():
    # 测试进度条渲染
    html = render_progress_bar(85, 100)
    assert "85%" in html
    assert "progress" in html.lower()

def test_render_skill_tags():
    # 测试技能标签渲染
    skills = ["Python", "Java", "SQL"]
    html = render_skill_tags(skills)
    assert "Python" in html
    assert "tag" in html.lower()

def test_render_score_card():
    # 测试分数卡片渲染
    html = render_score_card(85, "高度匹配")
    assert "85" in html
    assert "高度匹配" in html
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_ui_enhanced.py -v`
Expected: FAIL with "render_progress_bar not defined"

- [ ] **Step 3: 实现UI增强组件**

```python
# ui.py 添加新函数
def render_progress_bar(value: int, max_value: int = 100) -> str:
    """渲染进度条"""
    percentage = int((value / max_value) * 100)
    color = "#10B981" if percentage >= 80 else "#F59E0B" if percentage >= 60 else "#EF4444"
    
    return f'''
    <div style="background: #334155; border-radius: 6px; height: 8px; overflow: hidden;">
        <div style="height: 100%; border-radius: 6px; width: {percentage}%; background: {color}; transition: width 0.3s;"></div>
    </div>
    <div style="text-align: right; font-size: 0.8rem; color: {color}; margin-top: 4px;">{percentage}%</div>
    '''

def render_skill_tags(skills: List[str], max_show: int = 5) -> str:
    """渲染技能标签"""
    if not skills:
        return ""
    
    tags_html = ""
    for i, skill in enumerate(skills[:max_show]):
        tags_html += f'<span class="tag-match" style="margin: 2px;">✓ {skill}</span>'
    
    if len(skills) > max_show:
        tags_html += f'<span style="color: #64748B; font-size: 0.85rem;"> +{len(skills) - max_show} more</span>'
    
    return tags_html

def render_score_card(score: int, label: str) -> str:
    """渲染分数卡片"""
    color = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
    
    return f'''
    <div class="card" style="text-align: center; padding: 1.5rem;">
        <div class="score-big" style="color: {color}; font-size: 3rem;">{score}</div>
        <div style="color: {color}; font-size: 1rem; margin-top: 0.5rem;">{label}</div>
    </div>
    '''

def render_match_summary(match_result: dict) -> str:
    """渲染匹配摘要"""
    score = match_result.get('overall_score', 0)
    matched = match_result.get('matched', [])
    missing = match_result.get('missing', [])
    
    color = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
    label = "高度匹配" if score >= 90 else "较好匹配" if score >= 70 else "一般匹配" if score >= 50 else "匹配度低"
    
    html = f'''
    <div class="card">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="score-big" style="color: {color};">{score}</div>
            <div>
                <div style="color: {color}; font-weight: 600;">{label}</div>
                <div style="color: #64748B; font-size: 0.9rem;">匹配度评分</div>
            </div>
        </div>
        <div style="margin-top: 1rem;">
            {render_progress_bar(score)}
        </div>
    '''
    
    if matched:
        html += f'''
        <div style="margin-top: 1rem;">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">匹配技能:</div>
            {render_skill_tags([m.get('requirement', '') for m in matched])}
        </div>
        '''
    
    if missing:
        html += f'''
        <div style="margin-top: 1rem;">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">缺失技能:</div>
            {render_skill_tags([m.get('requirement', '') for m in missing], 3)}
        </div>
        '''
    
    html += '</div>'
    return html
```

- [ ] **Step 4: 更新主应用使用新UI组件**

```python
# app.py 更新页面渲染
def render_match_results_enhanced(results: List[MatchResult], mode: str):
    """显示增强的匹配结果"""
    for i, r in enumerate(results):
        match_result = {
            'overall_score': r.overall_score,
            'matched': [{'requirement': m.requirement} for m in r.matched],
            'missing': [{'requirement': m.requirement} for m in r.missing]
        }
        
        st.markdown(render_match_summary(match_result), unsafe_allow_html=True)
        
        # 添加详细信息展开
        with st.expander(f"查看详细分析 - {r.company}"):
            st.markdown(f"**公司:** {r.company}")
            st.markdown(f"**职位:** {r.position}")
            st.markdown(f"**地点:** {r.location}")
            st.markdown(f"**分析:** {r.analysis}")
            
            if r.optimization:
                st.markdown("**优化建议:**")
                for opt in r.optimization:
                    st.markdown(f"- {opt.get('original', '')} → {opt.get('suggested', '')}")
        
        btn_label = "🛡️ 面试准备" if mode == "shield" else "⚔️ 验证出题"
        if st.button(btn_label, key=f"prep_{mode}_{i}", use_container_width=True):
            st.session_state.selected_idx = i
            st.session_state.page = "prep"
            st.session_state.prep_result = None
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_ui_enhanced.py -v`
Expected: PASS

- [ ] **Step 6: 提交更改**

```bash
git add ui.py app.py tests/test_ui_enhanced.py
git commit -m "feat: enhance UI with progress bars, skill tags, and score cards"
```

---

## Task 6: 集成测试和最终验证

**Files:**
- Test: All files

- [ ] **Step 1: 运行完整测试套件**

Run: `pytest tests/ -v --cov=. --cov-report=term-missing`

- [ ] **Step 2: 测试应用功能**

Run: `streamlit run app.py`

验证：
- 简历解析准确性提升
- 匹配算法优化
- 面试模拟质量增强
- 数据持久化功能正常
- 用户界面改进

- [ ] **Step 3: 最终提交**

```bash
git add .
git commit -m "feat: complete all enhancements - parsing, matching, interview, persistence, UI"
```

---

## 完成

所有功能改进完成！项目现在具有：

1. **提升的简历解析准确性** - 技能和成就自动提取
2. **优化的匹配算法** - 技能和经验匹配度计算
3. **增强的面试模拟质量** - 追问生成和回答质量评估
4. **数据持久化** - SQLite数据库存储用户数据
5. **改进的用户界面** - 进度条、技能标签、分数卡片

**下一步建议：**
1. 添加用户认证系统
2. 实现数据导出功能
3. 添加更多面试题库
4. 优化移动端适配
5. 添加多语言支持
