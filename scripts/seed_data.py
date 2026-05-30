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
    {"name": "数学", "code": "math", "color": "#4ECDC4", "sort_order": 1},
    {"name": "英语", "code": "english", "color": "#FF6B6B", "sort_order": 2},
    {"name": "政治", "code": "politics", "color": "#E8734A", "sort_order": 3},
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
