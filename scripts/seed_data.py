"""
初始数据填充脚本 — 预置科目数据

用法:
    python scripts/seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import Subject

SUBJECTS = [
    {"name": "英语二", "code": "english", "color": "#FF6B6B", "sort_order": 1},
    {"name": "数学二", "code": "math", "color": "#4ECDC4", "sort_order": 2},
    {"name": "数据结构", "code": "ds", "color": "#45B7D1", "sort_order": 3},
    {"name": "计算机组成原理", "code": "co", "color": "#FF8A65", "sort_order": 4},
    {"name": "操作系统", "code": "os", "color": "#9575CD", "sort_order": 5},
    {"name": "计算机网络", "code": "cn", "color": "#4DB6AC", "sort_order": 6},
]


def seed_subjects():
    app = create_app()
    with app.app_context():
        db.create_all()  # 确保表存在

        for s in SUBJECTS:
            existing = Subject.query.filter_by(code=s["code"]).first()
            if existing:
                print(f"[跳过] 科目已存在: {s['name']}")
            else:
                subject = Subject(**s)
                db.session.add(subject)
                print(f"[新增] {s['name']} ({s['code']}) — {s['color']}")

        db.session.commit()

        count = Subject.query.count()
        print(f"\n科目表共 {count} 条记录")


if __name__ == "__main__":
    seed_subjects()
