"""
408拆分：将"408计算机综合"替换为4门独立科目
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import Subject, ExamQuestion

NEW_SUBJECTS = [
    {"name": "英语二", "code": "english", "color": "#FF6B6B", "sort_order": 1},
    {"name": "数学二", "code": "math", "color": "#4ECDC4", "sort_order": 2},
    {"name": "数据结构", "code": "ds", "color": "#45B7D1", "sort_order": 3},
    {"name": "计算机组成原理", "code": "co", "color": "#FF8A65", "sort_order": 4},
    {"name": "操作系统", "code": "os", "color": "#9575CD", "sort_order": 5},
    {"name": "计算机网络", "code": "cn", "color": "#4DB6AC", "sort_order": 6},
]

app = create_app()
with app.app_context():
    # 1. 先确保6个科目都存在
    for s in NEW_SUBJECTS:
        existing = Subject.query.filter_by(code=s["code"]).first()
        if not existing:
            db.session.add(Subject(**s))
    db.session.commit()

    # 2. 把旧408的题目迁移到数据结构
    old_cs = Subject.query.filter_by(code="cs").first()
    ds = Subject.query.filter_by(code="ds").first()
    if old_cs and ds:
        count = ExamQuestion.query.filter_by(subject_id=old_cs.id).count()
        if count > 0:
            ExamQuestion.query.filter_by(subject_id=old_cs.id).update(
                {"subject_id": ds.id}, synchronize_session=False
            )
            print(f"已将 {count} 道题目从408迁移到数据结构")

    # 3. 删除旧408科目
    if old_cs:
        db.session.delete(old_cs)
        db.session.commit()
        print("已删除旧科目: 408计算机综合")

    # 4. 更新所有科目信息
    for s in NEW_SUBJECTS:
        subj = Subject.query.filter_by(code=s["code"]).first()
        if subj:
            subj.name = s["name"]
            subj.color = s["color"]
            subj.sort_order = s["sort_order"]
    db.session.commit()

    print("\n当前科目：")
    for s in Subject.query.order_by(Subject.sort_order).all():
        q_count = ExamQuestion.query.filter_by(subject_id=s.id).count()
        print(f"  {s.sort_order}. {s.name} ({s.code}) — {q_count} 题")
