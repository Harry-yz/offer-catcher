# Offer Catcher 架构重构设计文档

## 1. 概述

### 1.1 项目背景
Offer Catcher 是一个基于 Streamlit 的求职辅助工具，提供简历解析、JD匹配、面试准备等功能。当前代码全部集中在 app.py 文件中（720行），随着功能增加，代码可维护性下降。

### 1.2 重构目标
- 提高代码可维护性和可扩展性
- 改善错误处理和日志记录
- 增强安全性（API密钥保护）
- 为后续功能改进奠定基础

## 2. 架构设计

### 2.1 模块划分

#### 2.1.1 api.py - API调用层
**职责：**
- 封装所有外部API调用（MiMo API）
- 处理请求/响应格式转换
- 实现重试机制和错误处理
- 管理API密钥和配置

**主要函数：**
- api(messages, model=None, json_mode=False)
- extract_json(text)
- parse_image(file_bytes, prompt)
- parse_text(text, prompt)
- pdf_to_text(file_bytes)

#### 2.1.2 parser.py - 解析逻辑层
**职责：**
- 简历解析（PDF、图片、文本）
- JD解析（图片、文本）
- 数据标准化和验证
- 解析结果缓存

**主要函数：**
- do_parse_resume(uploaded_file)
- do_parse_jd(uploaded_file=None, text_input='')
- validate_resume_data(data)
- validate_jd_data(data)

#### 2.1.3 ui.py - 界面组件层
**职责：**
- Streamlit UI组件封装
- 页面布局和样式
- 用户交互处理
- 状态管理

**主要组件：**
- render_upload_panel(role)
- render_parsed()
- render_match_results(mode)
- render_portal()
- render_seeker()
- render_interviewer()
- render_prep()

#### 2.1.4 config.py - 配置管理层
**职责：**
- API配置（URL、模型、密钥）
- 提示词管理
- Fallback数据
- 环境变量处理

#### 2.1.5 models.py - 数据模型层
**职责：**
- 定义数据结构（使用dataclasses或Pydantic）
- 类型提示和验证
- 数据序列化/反序列化

**主要模型：**
- Resume: 简历数据
- JobDescription: 职位描述数据
- MatchResult: 匹配结果数据

### 2.2 数据流

用户输入 → UI层 → 解析层 → API层 → 外部API
    ↓
解析结果 → 数据模型 → 匹配逻辑 → UI展示
    ↓
面试准备 → API层 → 外部API → UI展示

### 2.3 错误处理策略

#### 2.3.1 分层错误处理
- API层：捕获网络错误、API限流、认证失败
- 解析层：捕获文件格式错误、解析失败、数据验证错误
- UI层：显示用户友好的错误信息，提供重试选项

#### 2.3.2 日志记录
- 使用Python标准库logging模块
- 不同级别：DEBUG、INFO、WARNING、ERROR
- 记录到文件和控制台

### 2.4 安全性改进

#### 2.4.1 API密钥保护
- 创建.gitignore文件，排除敏感文件
- 使用环境变量或Streamlit secrets
- 不在代码中硬编码密钥

#### 2.4.2 输入验证
- 验证上传文件类型和大小
- 清理用户输入，防止注入攻击
- 限制API调用频率

## 3. 实施计划

### 3.1 阶段1：基础重构（1-2天）
1. 创建模块文件结构
2. 迁移核心函数到相应模块
3. 更新导入关系
4. 确保基本功能正常

### 3.2 阶段2：数据模型（1天）
1. 定义数据模型类
2. 添加类型提示
3. 实现数据验证
4. 更新解析函数使用新模型

### 3.3 阶段3：错误处理（1天）
1. 实现分层错误处理
2. 添加日志记录
3. 改进用户错误提示
4. 添加重试机制

### 3.4 阶段4：安全性改进（0.5天）
1. 创建.gitignore
2. 检查并保护API密钥
3. 添加输入验证
4. 实现基本的安全措施

### 3.5 阶段5：测试和文档（1天）
1. 编写单元测试
2. 添加代码注释
3. 创建README文档
4. 更新依赖管理

## 4. 风险评估

### 4.1 技术风险
- Streamlit限制：Streamlit的session state管理可能限制模块化程度
- 性能影响：模块化可能增加函数调用开销
- 兼容性：需要确保新旧代码兼容

### 4.2 缓解措施
- 保持Streamlit的session state在UI层管理
- 优化关键路径的函数调用
- 逐步迁移，确保每个阶段都可运行

## 5. 成功标准

### 5.1 代码质量
- 每个模块不超过300行
- 函数平均复杂度降低50%
- 测试覆盖率达到60%以上

### 5.2 可维护性
- 新功能开发时间减少30%
- Bug修复时间减少40%
- 代码审查效率提高50%

### 5.3 用户体验
- 错误提示更加友好
- 响应时间保持稳定
- 功能完整性保持100%

## 6. 后续改进

### 6.1 功能改进
- 提升简历解析准确性
- 优化匹配算法
- 增强面试模拟质量
- 添加数据持久化

### 6.2 技术改进
- 添加缓存机制
- 实现异步处理
- 优化API调用效率
- 添加监控和告警

## 7. 附录

### 7.1 文件结构
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

### 7.2 依赖版本
streamlit>=1.28.0
openai>=1.0.0
Pillow>=9.0.0
PyPDF2>=3.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0

### 7.3 配置示例
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv('API_BASE', 'https://token-plan-cn.xiaomimimo.com/v1')
MODEL = os.getenv('MODEL', 'mimo-v2.5-pro')
MIMO_API_KEY = os.getenv('MIMO_API_KEY')

---

**设计者：** OpenCode AI  
**日期：** 2026-05-30  
**版本：** 1.0
