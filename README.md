# Offer Catcher - AI求职智能匹配平台

## 功能特性

- 🎯 **智能岗位匹配** - 上传简历+多个JD，AI分析匹配度
- 🛡️ **智能面试准备** - 上传简历+1个JD，生成面试题库
- ⚔️ **候选人深度验证** - 面试官模式，生成面试策略

## 快速开始

### 本地运行

```bash
# 1. 克隆项目
git clone <repository-url>
cd AIHR

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入API密钥

# 4. 启动服务
python server.py

# 5. 访问应用
# http://localhost:8080
```

## 技术栈

- **后端:** Python + Flask
- **前端:** HTML + CSS + JavaScript
- **AI服务:** MinerU (文档解析) + MiMo (AI推理)
- **缓存:** 文件缓存

## 项目结构

```
AIHR/
├── server.py           # Flask主入口
├── api.py              # API调用层
├── parser.py           # 解析逻辑层
├── config.py           # 配置管理
├── models.py           # 数据模型
├── mineru_parser.py    # MinerU封装
├── cache_manager.py    # 缓存管理
├── api/index.py        # Vercel入口
├── templates/          # Flask模板
├── tests/              # 单元测试
├── .env.example        # 环境变量示例
├── vercel.json         # Vercel配置
└── requirements.txt    # 依赖清单
```

## API接口

- `POST /api/parse` - 解析简历和JD
- `POST /api/match` - 匹配分析
- `POST /api/interview` - 生成面试准备
- `POST /api/mock` - 模拟面试追问

## 许可证

MIT License
