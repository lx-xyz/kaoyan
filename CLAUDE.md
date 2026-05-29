# 考研一体化学习辅助系统 — AI 助手指引

## 项目简介
为 22408（计算机专硕）考研学生打造的网页版一体化学习辅助系统。
科目：英语二、数学二、408计算机综合。

## 规范文档路径

| 文档 | 路径 | 用途 |
|------|------|------|
| 功能需求 | `docs/requirements.md` | 各模块功能描述、验收标准 |
| 技术栈 | `docs/tech_stack.md` | 选型理由、版本要求 |
| 数据库设计 | `docs/database_design.md` | 所有表字段、关联关系 |
| UI设计规范 | `docs/ui_design_spec.md` | 色值、字体、组件样式 |
| 开发阶段 | `docs/development_phases.md` | 分阶段执行步骤和验证标准 |
| API设计 | `docs/api_design.md` | 所有路由和接口定义 |
| 部署指南 | `docs/deployment.md` | 本地运行和部署步骤 |

## 工作流程

1. **开始工作前**：读取 `dev_logs/` 中最新的日志，了解当前进度
2. **按阶段开发**：严格按 `docs/development_phases.md` 中的阶段顺序推进
3. **每步验证**：完成一个步骤后验证通过再继续下一步
4. **每日记录**：每天工作结束前更新 `dev_logs/YYYY-MM-DD.md`
5. **问题优先**：不在问题未解决时继续推进

## 代码规范

- Python 使用 Flask 3.1+，遵循 PEP 8 风格
- 前端使用 Jinja2 模板 + Bootstrap 5.3，黄色主题 `#FFA000`
- 数据库使用 SQLAlchemy ORM，禁止手写 SQL
- 路由按模块拆分到 `app/routes/` 下的独立文件
- 复用的业务逻辑放在 `app/services/`

## 安全规则

- 密码 MUST 使用 Flask-Bcrypt 加密存储，不存明文
- 所有用户输入 MUST 经过验证和转义（Flask-WTF 自动处理）
- 敏感配置（SECRET_KEY 等）放在 `config.py`，不硬编码
- 数据库操作使用 ORM 参数化查询，防止 SQL 注入
- 生产环境 MUST 更换 SECRET_KEY

## 项目结构

```
考研学习系统/
├── CLAUDE.md               ← 本文件
├── app.py                  # 应用入口
├── config.py               # 配置
├── requirements.txt        # 依赖
├── docs/                   # 规范文档
├── dev_logs/               # 开发日志
├── scripts/                # 工具脚本
├── app/
│   ├── __init__.py         # Flask 工厂 + 扩展初始化
│   ├── models.py           # 数据库模型
│   ├── forms.py            # WTForm 表单
│   ├── routes/             # 路由模块
│   ├── services/           # 业务逻辑
│   ├── templates/          # Jinja2 模板
│   └── static/             # CSS/JS/图片
├── migrations/             # 数据库迁移
└── uploads/                # 用户上传
```

## 当前状态

- **阶段**：5 — 题目管理+手动录入（已完成）
- **已完成**：阶段0/1/2/5 — 骨架、数据库、用户系统、题目CRUD+KaTeX
- **下一步**：阶段6 — 做题功能（逐题练习、自动判分、错题自动入错题本）

## 运行方式

```bash
# 本地开发
python app.py
# 浏览器打开 http://127.0.0.1:5000
```
