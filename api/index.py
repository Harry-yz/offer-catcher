# api/index.py
"""
Vercel Serverless Function入口
"""

import sys
import os

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加项目根目录到Python路径
sys.path.insert(0, ROOT_DIR)

# 设置环境变量
os.environ['VERCEL'] = '1'
os.environ['ROOT_DIR'] = ROOT_DIR

# 导入Flask应用
from server import app

# Vercel需要这个handler
handler = app
