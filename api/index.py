# api/index.py
"""
Vercel Serverless Function入口
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 设置环境变量
os.environ['VERCEL'] = '1'

# 导入Flask应用
from server import app

# Vercel需要这个handler
handler = app
