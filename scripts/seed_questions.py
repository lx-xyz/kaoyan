"""
预置示例题目数据
用法: python scripts/seed_questions.py
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import Subject, ExamQuestion


def seed():
    app = create_app()
    with app.app_context():
        # 清空旧题
        ExamQuestion.query.delete()
        db.session.commit()

        math_id = Subject.query.filter_by(code="math").first().id
        ds_id = Subject.query.filter_by(code="ds").first().id
        co_id = Subject.query.filter_by(code="co").first().id
        os_id = Subject.query.filter_by(code="os").first().id
        cn_id = Subject.query.filter_by(code="cn").first().id
        eng_id = Subject.query.filter_by(code="english").first().id

        questions = [
            ExamQuestion(
                subject_id=math_id, year=2024, source="2024年真题",
                question_type="填空", question_number=1,
                title="计算极限 $\\lim_{x \\to 0} \\frac{\\sin x}{x}$",
                correct_answer="1",
                analysis="重要极限：$\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1$",
                difficulty=2, tags="极限", created_by=1,
            ),
            ExamQuestion(
                subject_id=math_id, year=2024, source="2024年真题",
                question_type="单选", question_number=2,
                title="设 $f(x) = x^2$，则 $f'(1) =$",
                option_a="0", option_b="1", option_c="2", option_d="3",
                correct_answer="C",
                analysis="$f'(x) = 2x$，代入 $x=1$ 得 $f'(1) = 2$",
                difficulty=2, tags="导数", created_by=1,
            ),
            ExamQuestion(
                subject_id=math_id, year=2023, source="2023年真题",
                question_type="解答", question_number=5,
                title="计算不定积分 $\\int x e^x \\, dx$",
                correct_answer="(x-1)e^x + C",
                analysis="使用分部积分法：设 $u=x$, $dv=e^x dx$，则 $du=dx$, $v=e^x$，得 $\\int x e^x dx = x e^x - \\int e^x dx = (x-1)e^x + C$",
                difficulty=3, tags="积分,分部积分", created_by=1,
            ),
            ExamQuestion(
                subject_id=ds_id, year=2024, source="2024年408真题",
                question_type="单选", question_number=1,
                title="下列排序算法中，时间复杂度为 $O(n \\log n)$ 且是稳定排序的是？",
                option_a="快速排序", option_b="归并排序",
                option_c="堆排序", option_d="希尔排序",
                correct_answer="B",
                analysis="归并排序时间复杂度 $O(n \\log n)$，且是稳定排序。快速排序和堆排序是不稳定排序，希尔排序时间复杂度取决于增量序列。",
                difficulty=3, tags="排序,算法", created_by=1,
            ),
            ExamQuestion(
                subject_id=os_id, year=2024, source="2024年408真题",
                question_type="单选", question_number=5,
                title="在分页存储管理系统中，页表的作用是？",
                option_a="管理内存与外存之间的数据交换",
                option_b="实现逻辑地址到物理地址的映射",
                option_c="记录每个进程的CPU时间",
                option_d="缓存最近访问的页面",
                correct_answer="B",
                analysis="页表用于记录逻辑页号到物理页框号的映射关系，实现地址转换。TLB是快表(选项D)，交换空间管理负责选项A。",
                difficulty=3, tags="操作系统,内存管理", created_by=1,
            ),
            ExamQuestion(
                subject_id=eng_id, year=2024, source="2024年英语二真题",
                question_type="完形", question_number=1,
                title="In recent years, artificial intelligence has ____ significant progress in various fields.",
                option_a="made", option_b="done",
                option_c="taken", option_d="given",
                correct_answer="A",
                analysis='"make progress" 是固定搭配，表示"取得进展"。其他选项不与progress搭配。',
                difficulty=2, tags="完形,搭配", created_by=1,
            ),
        ]

        for q in questions:
            db.session.add(q)
        db.session.commit()

        count = ExamQuestion.query.count()
        print(f"预置题目完成，共 {count} 道")
        for q in ExamQuestion.query.all():
            print(f"  [{q.subject.name}] {q.question_type} — {q.title[:50]}...")


if __name__ == "__main__":
    seed()
