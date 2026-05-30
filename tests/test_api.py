# tests/test_api.py
import pytest
from api import extract_json, APIError

def test_extract_json_direct():
    text = '{"name": "张三", "age": 25}'
    result = extract_json(text)
    assert result == {"name": "张三", "age": 25}

def test_extract_json_from_markdown():
    text = '```json\n{"name": "张三"}\n```'
    result = extract_json(text)
    assert result == {"name": "张三"}

def test_extract_json_from_mixed():
    text = '这是分析结果：\n{"score": 85}\n请参考'
    result = extract_json(text)
    assert result == {"score": 85}

def test_extract_json_invalid():
    text = '这不是JSON格式'
    result = extract_json(text)
    assert result == {}

def test_api_error():
    with pytest.raises(APIError):
        raise APIError("测试错误")
