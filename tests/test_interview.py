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
