# to-do-list

# Smart Task Manager 🚀
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.2-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)

> 2025 Mini Hackathon 48 Hour Development Work 
<img src="screenshots/demo.gif" width="800" alt="系统演示">

## 🏆 Project Highlights
- 48 hours of rapid prototyping
- Innovative combination of the four quadrants of time management
- Intelligent Scheduling Algorithm
- Full Stack Technology Integration Practice

## ✨ Core Functionality
### Intelligent Task Management
- Four-quadrant prioritization classification (importance/urgency matrix)
- Adaptive time estimation algorithm (画饼)
- Intelligent schedule conflict detection (画饼)
- Automatic commute time calculation (画饼)

### Deep Integration
- Google Calendar two-way synchronization
- Geolocation services integration (画饼)
- Multi-device real-time synchronization (画饼)

### Efficiency Tools
- One-click smart sorting
- Visual Data Kanban (画饼)
- Multi-dimensional task filtering
- CSV/Excel Import and Export (画饼)

## 🛠️ 技术栈
**Frontend**  
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?logo=javascript)

**Backend**  
![Flask](https://img.shields.io/badge/Flask-2.3.2-000000?logo=flask)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3.0-29ABE2)

**Database**  
![SQLite](https://img.shields.io/badge/SQLite-3.42-003B57?logo=sqlite)

**APIs**  
![Google Calendar API](https://img.shields.io/badge/Google%20Calendar%20API-v3-4285F4?logo=googlecalendar)

## 🚀 Quick Start
### Environmental requirements
- Python 3.9+
- Google API凭证文件

### Installation steps
```bash
# 克隆仓库
git clone https://github.com/Shi-330/to_do_list.git

# 安装依赖
pip install -r requirements.txt

# 配置Google API
1. 前往Google Cloud Console创建项目
2. 启用Calendar API并下载credentials.json
3. 将文件放置于项目根目录

# 启动服务
flask run
