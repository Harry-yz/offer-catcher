import sys
sys.path.insert(0, '.')
from api import extract_json, APIError

def test_extract_json_direct():
    text = '{"name": "张三", "age": 25}'
    result = extract_json(text)
    assert result == {"name": "张三", "age": 25}
    print('test_extract_json_direct 通过')

def test_extract_json_from_markdown():
    text = '```json\n{"name": "张三"}\n```'
    result = extract_json(text)
    assert result == {"name": "张三"}
    print('test_extract_json_from_markdown 通过')

def test_extract_json_from_mixed():
    text = '这是分析结果：\n{"score": 85}\n请参考'
    result = extract_json(text)
    assert result == {"score": 85}
    print('test_extract_json_from_mixed 通过')

def test_extract_json_invalid():
    text = '这不是JSON格式'
    result = extract_json(text)
    assert result == {}
    print('test_extract_json_invalid 通过')

def test_api_error():
    try:
        raise APIError('测试错误')
    except APIError:
        print('test_api_error 通过')

test_extract_json_direct()
test_extract_json_from_markdown()
test_extract_json_from_mixed()
test_extract_json_invalid()
test_api_error()
print('所有API测试通过')
