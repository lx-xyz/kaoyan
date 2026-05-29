"""
每日开发日志生成脚本

用法:
    python scripts/daily_log.py

功能:
    1. 检测 dev_logs/ 下是否有当天日期的日志
    2. 如果没有 → 从模板生成新日志
    3. 如果有 → 提示已存在，不覆盖
"""

import os
import sys
from datetime import date

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "dev_logs")

LOG_TEMPLATE = """# 开发日志 — {date_cn}

## 当前阶段
阶段 0 — 项目初始化

## 今日完成
- [x] 项目目录结构创建
- [x] requirements.txt 依赖安装
- [x] Flask 应用骨架搭建并运行成功
- [x] 基础路由和模板创建
- [x] 黄色主题 CSS 完成
- [x] docs/ 规范文档完成

## 待办事项
- [ ] 进入阶段1：数据库模型定义
- [ ] 创建 models.py 所有表
- [ ] 初始化数据库迁移

## 遇到的问题
- Flask-Login 需要 user_loader 回调，先用占位函数解决
- Config.BASE_DIR 引用方式修正为模块级导入

## 下一步计划
开始阶段1 — 创建数据库模型
"""


def main():
    today = date.today()
    filename = f"{today.isoformat()}.md"
    filepath = os.path.join(LOGS_DIR, filename)

    os.makedirs(LOGS_DIR, exist_ok=True)

    if os.path.exists(filepath):
        print(f"[跳过] 今日日志已存在: dev_logs/{filename}")
        return

    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    date_cn = f"{today.year}年{today.month:02d}月{today.day:02d}日 星期{weekdays[today.weekday()]}"

    content = LOG_TEMPLATE.format(date_cn=date_cn)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[完成] 今日日志已生成: dev_logs/{filename}")


if __name__ == "__main__":
    main()
