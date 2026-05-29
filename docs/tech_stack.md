# 技术栈说明

## 选型总览

| 层级 | 技术 | 版本 | 职责 |
|------|------|------|------|
| 后端框架 | Flask | 3.1.x | Web 请求处理、路由 |
| ORM | SQLAlchemy (Flask-SQLAlchemy) | 3.1.x | 数据库操作，不用手写 SQL |
| 数据库(开发) | SQLite | - | 零配置，开发环境直接用 |
| 数据库(部署) | PostgreSQL | 15+ | 生产环境 |
| 用户认证 | Flask-Login | 0.6.x | 登录会话管理 |
| 密码加密 | Flask-Bcrypt | 1.0.x | bcrypt 加盐哈希 |
| 表单处理 | Flask-WTF + WTForms | 1.2.x / 3.1.x | 表单生成、验证、CSRF 保护 |
| 数据库迁移 | Flask-Migrate | 4.0.x | 表结构变更管理 |
| 前端框架 | Bootstrap 5.3 | 5.3.x | UI 组件和响应式布局 |
| 模板引擎 | Jinja2 | (Flask 内置) | 服务端渲染 HTML |
| 图表 | Chart.js | 4.x (CDN) | 学习统计图表 |
| 数学公式 | KaTeX | (CDN) | LaTeX 公式渲染 |
| Markdown | SimpleMDE | (CDN) | 笔记编辑器 |
| 表格处理 | pandas + openpyxl | 2.2.x / 3.1.x | Excel 导入解析 |
| WSGI 服务器 | Gunicorn | 22.x | 部署时用 |

## 为什么不选前后端分离

- 用户是编程初学者，前后端分离需要学两套体系
- 服务端渲染（Jinja2）一个 `python app.py` 就能跑
- 3科题库数据量不大，SSR 性能完全够用
- 减少 API 设计、跨域处理等复杂问题

## 开发环境要求

- Python 3.11+
- Windows 10/11
- 所有依赖见 `requirements.txt`
- 安装命令：`pip install -r requirements.txt`
