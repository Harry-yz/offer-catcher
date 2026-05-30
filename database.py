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
