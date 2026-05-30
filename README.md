# Offer Catcher (Offer捕手)

AI求职智能匹配工具 - 求职者之盾 vs 面试官之矛

## 功能特性

- 📄 **简历解析**: 支持PDF、图片格式简历解析
- 🎯 **JD解析**: 支持图片、文本格式职位描述解析
- 📊 **匹配分析**: 智能分析简历与JD的匹配度
- 🛡️ **求职者之盾**: 面试准备、自我介绍、面试题库
- ⚔️ **面试官之矛**: 候选人验证、破绽识别、深度追问

## 安装

1. 克隆项目
```bash
git clone <repository-url>
cd AIHR
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置API密钥
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加API密钥
MIMO_API_KEY=your-api-key-here
```

## 使用

1. 启动应用
```bash
streamlit run app.py
```

2. 访问应用
打开浏览器访问 `http://localhost:8501`

3. 使用流程
- 选择模式（求职者/面试官）
- 上传简历PDF/图片
- 输入或上传目标JD
- 点击解析 → 查看解析结果
- 点击匹配 → 查看匹配排名
- 点击岗位 → 进入面试准备/验证出题

## 项目结构

```
AIHR/
├── app.py              # 主入口，路由和状态管理
├── api.py              # API调用层
├── parser.py           # 解析逻辑层
├── ui.py               # 界面组件层
├── config.py           # 配置管理层
├── models.py           # 数据模型层
├── .gitignore          # Git忽略文件
├── requirements.txt    # 依赖管理
├── README.md           # 项目文档
└── tests/              # 测试目录
    ├── test_api.py
    ├── test_parser.py
    └── test_models.py
```

## 开发

### 运行测试
```bash
pytest tests/ -v
```

### 代码风格
```bash
# 使用black格式化
black .

# 使用flake8检查
flake8 .
```

## 配置

### 环境变量
- `MIMO_API_KEY`: MiMo API密钥
- `API_BASE`: API基础URL（默认: https://token-plan-cn.xiaomimimo.com/v1）
- `MODEL`: 使用的模型（默认: mimo-v2.5-pro）

### Streamlit配置
在 `.streamlit/secrets.toml` 中配置API密钥：
```toml
MIMO_API_KEY = "your-api-key-here"
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
