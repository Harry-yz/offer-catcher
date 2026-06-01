# Offer Catcher 部署说明

## 1Panel部署步骤

### 1. 上传文件

将整个 `deploy_package` 目录上传到服务器的 `/www/wwwroot/offer-catcher`

### 2. 安装依赖

```bash
cd /www/wwwroot/offer-catcher
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：
```bash
cp .env.example .env
nano .env
```

填入你的API密钥：
```
MIMO_API_KEY=你的MiMo API密钥
MINERU_API_KEY=你的MinerU API密钥
API_BASE=https://api.xiaomimimo.com/v1
MODEL=mimo-v2.5-pro
```

### 4. 测试运行

```bash
python server.py
```

访问 http://服务器IP:8080 测试

### 5. 1Panel配置Python项目

1. 进入 1Panel → **网站** → **Python项目**
2. 点击 **新建项目**
3. 配置：
   - **项目名称：** offer-catcher
   - **项目路径：** /www/wwwroot/offer-catcher
   - **Python版本：** 3.10+
   - **启动命令：** python server.py
   - **端口：** 8080
   - **环境变量：** 填入.env中的内容

### 6. 配置Nginx反向代理（可选）

如果要通过域名访问：
1. 进入 1Panel → **网站** → **你的网站**
2. 点击 **反向代理**
3. 添加反向代理：
   - **名称：** offer-catcher
   - **代理地址：** http://127.0.0.1:8080
   - **路径：** /offer-catcher

### 7. 访问

- 直接访问：http://服务器IP:8080
- 域名访问：https://你的域名/offer-catcher

## 文件结构

```
offer-catcher/
├── server.py           # Flask主入口
├── api.py              # API调用层
├── parser.py           # 解析逻辑层
├── config.py           # 配置管理
├── models.py           # 数据模型
├── mineru_parser.py    # MinerU封装
├── cache_manager.py    # 缓存管理
├── templates/          # Flask模板
│   ├── index.html      # 首页
│   ├── workbench.html  # 岗位匹配/候选人验证
│   └── workbench_interview.html  # 面试准备
├── static/             # 静态文件
├── requirements.txt    # 依赖清单
├── .env.example        # 环境变量示例
└── DEPLOY.md           # 本文件
```

## 常见问题

### Q: 启动失败怎么办？
A: 检查Python版本（需要3.10+），检查依赖是否安装完整

### Q: API调用失败怎么办？
A: 检查.env文件中的API密钥是否正确

### Q: 端口被占用怎么办？
A: 修改server.py中的端口号，或在1Panel中修改启动命令

### Q: 如何更新？
A: 上传新文件后重启Python项目
