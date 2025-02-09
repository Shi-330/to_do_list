# to-do-list

# Smart Task Manager 🚀
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.2-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)

> 2025 Mini Hackathon 48 Hour Development Work 
<img src="screenshots/demo.gif" width="800" alt="系统演示">

## 🏆 项目亮点
- 48小时极速开发原型
- 创新结合时间管理四象限法则
- 智能日程编排算法
- 全栈技术整合实践

## ✨ 核心功能
### 智能任务管理
- 四象限优先级分类（重要/紧急矩阵）
- 自适应时间估算算法（画饼）
- 智能日程冲突检测（画饼）
- 通勤时间自动计算（画饼）

### 深度集成
- Google Calendar双向同步
- 地理位置服务整合（画饼）
- 多设备实时同步（画饼）

### 效率工具
- 一键智能排序
- 可视化数据看板（画饼）
- 多维度任务筛选
- CSV/Excel导入导出（画饼）

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

## 🚀 快速开始
### 环境要求
- Python 3.9+
- Google API凭证文件

### 安装步骤
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
