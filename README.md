内容：
# Life Number Report - 生命数字解读报告
一个基于AI的生命数字解读报告生成网站。
## 快速开始
### 1. 安装依赖
```bash
pip install -r requirements.txt

### 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key

### 3. 运行
python app.py

访问 http://localhost:5000

### 4. 部署
推荐使用 Railway 或 Render:
Railway: 直接连接 GitHub 仓库
Render: 选择 Web Service，命令 `gunicorn app:app`
## 功能
[x] 生命数字计算
[x] AI报告生成
[ ] 兑换码系统（开发中）
[ ] 历史记录（开发中）
## 技术栈
前端: 原生 HTML/CSS/JavaScript
后端: Python Flask
数据库: SQLite
AI: MiniMax
