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
