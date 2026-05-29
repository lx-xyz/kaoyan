"""
示例题目种子脚本 — 覆盖所有科目
用法: python scripts/seed_demo_questions.py
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import Subject, ExamQuestion

QUESTIONS = {
    "math": [
        {
            "year": 2024, "source": "示例-数学",
            "question_type": "单选", "question_number": 1,
            "title": "设函数 $f(x)=x^3-3x$，则 $f(x)$ 的极大值为",
            "option_a": "-2", "option_b": "0", "option_c": "2", "option_d": "4",
            "correct_answer": "C",
            "analysis": "$f'(x)=3x^2-3=3(x-1)(x+1)$。$x=-1$处$f'$由正变负，极大值$f(-1)=2$",
            "difficulty": 2, "tags": "导数,极值",
        },
        {
            "year": 2024, "source": "示例-数学",
            "question_type": "填空", "question_number": 2,
            "title": "计算 $\\int_0^1 (2x+1)\\,dx =$",
            "correct_answer": "2",
            "analysis": "$\\int_0^1 (2x+1)dx = [x^2+x]_0^1 = 2$",
            "difficulty": 1, "tags": "积分",
        },
        {
            "year": 2023, "source": "示例-数学",
            "question_type": "解答", "question_number": 3,
            "title": "求微分方程 $y''+y=0$ 的通解",
            "correct_answer": "$y=C_1\\cos x + C_2\\sin x$",
            "analysis": "特征方程为$r^2+1=0$，$r=\\pm i$，通解为$y=C_1\\cos x + C_2\\sin x$",
            "difficulty": 3, "tags": "微分方程",
        },
        {
            "year": 2023, "source": "示例-数学",
            "question_type": "单选", "question_number": 4,
            "title": "设 $A$ 为3阶方阵，$|A|=2$，则 $|2A|=$",
            "option_a": "4", "option_b": "8", "option_c": "12", "option_d": "16",
            "correct_answer": "D",
            "analysis": "$|kA|=k^n|A|$，$n=3$，$|2A|=2^3\\times2=16$",
            "difficulty": 2, "tags": "线性代数,行列式",
        },
        {
            "year": 2023, "source": "示例-数学",
            "question_type": "填空", "question_number": 5,
            "title": "极限 $\\lim_{n\\to\\infty} \\frac{n^2+1}{2n^2-3} =$",
            "correct_answer": "$\\frac{1}{2}$",
            "analysis": "分子分母同除以$n^2$，$\\lim_{n\\to\\infty}\\frac{1+1/n^2}{2-3/n^2} = \\frac{1}{2}$",
            "difficulty": 1, "tags": "极限",
        },
    ],
    "ds": [
        {
            "year": 2024, "source": "示例-数据结构",
            "question_type": "单选", "question_number": 1,
            "title": "在长度为 $n$ 的顺序表中插入一个元素，平均需要移动多少个元素？",
            "option_a": "$n$", "option_b": "$n/2$", "option_c": "$n-1$", "option_d": "$\\log n$",
            "correct_answer": "B",
            "analysis": "顺序表插入时，等概率下平均移动$n/2$个元素",
            "difficulty": 1, "tags": "线性表",
        },
        {
            "year": 2024, "source": "示例-数据结构",
            "question_type": "单选", "question_number": 2,
            "title": "非空二叉树中，叶子结点数 $n_0$ 与度为2的结点数 $n_2$ 满足什么关系？",
            "option_a": "$n_0 = n_2$", "option_b": "$n_0 = n_2 + 1$", "option_c": "$n_2 = n_0 + 1$", "option_d": "$n_0 = 2n_2$",
            "correct_answer": "B",
            "analysis": "二叉树性质：$n_0 = n_2 + 1$",
            "difficulty": 2, "tags": "二叉树",
        },
        {
            "year": 2023, "source": "示例-数据结构",
            "question_type": "单选", "question_number": 3,
            "title": "下列排序算法中，时间复杂度为 $O(n\\log n)$ 且是稳定排序的是？",
            "option_a": "快速排序", "option_b": "归并排序", "option_c": "堆排序", "option_d": "希尔排序",
            "correct_answer": "B",
            "analysis": "归并排序$O(n\\log n)$且稳定；快排不稳定；堆排$O(n\\log n)$但不稳定",
            "difficulty": 3, "tags": "排序",
        },
    ],
    "co": [
        {
            "year": 2024, "source": "示例-组成原理",
            "question_type": "单选", "question_number": 1,
            "title": "在补码表示中，8位二进制数能表示的范围是？",
            "option_a": "$-127\\sim+127$", "option_b": "$-128\\sim+127$",
            "option_c": "$0\\sim255$", "option_d": "$-128\\sim+128$",
            "correct_answer": "B",
            "analysis": "8位补码范围：$-2^{7}\\sim 2^{7}-1$，即$-128\\sim+127$",
            "difficulty": 1, "tags": "数据表示",
        },
        {
            "year": 2024, "source": "示例-组成原理",
            "question_type": "单选", "question_number": 2,
            "title": "Cache与主存之间的地址映射方式不包括哪种？",
            "option_a": "直接映射", "option_b": "全相联映射", "option_c": "组相联映射", "option_d": "段页式映射",
            "correct_answer": "D",
            "analysis": "Cache映射方式有直接映射、全相联映射和组相联映射三种。段页式是虚拟存储器的管理方式。",
            "difficulty": 2, "tags": "Cache,存储系统",
        },
    ],
    "os": [
        {
            "year": 2024, "source": "示例-操作系统",
            "question_type": "单选", "question_number": 1,
            "title": "进程从运行态变为就绪态的原因是？",
            "option_a": "等待I/O完成", "option_b": "时间片用完", "option_c": "进程被创建", "option_d": "获得CPU",
            "correct_answer": "B",
            "analysis": "时间片用完→运行→就绪；等待I/O→运行→阻塞；进程创建→就绪",
            "difficulty": 1, "tags": "进程管理",
        },
        {
            "year": 2024, "source": "示例-操作系统",
            "question_type": "单选", "question_number": 2,
            "title": "在分页存储管理系统中，页表的作用是？",
            "option_a": "管理内存与外存交换", "option_b": "实现逻辑地址到物理地址映射",
            "option_c": "记录CPU时间", "option_d": "缓存最近页面",
            "correct_answer": "B",
            "analysis": "页表记录逻辑页号到物理页框号的映射，实现地址转换",
            "difficulty": 2, "tags": "内存管理",
        },
    ],
    "cn": [
        {
            "year": 2024, "source": "示例-计算机网络",
            "question_type": "单选", "question_number": 1,
            "title": "OSI参考模型中，负责路由选择的层是？",
            "option_a": "数据链路层", "option_b": "网络层", "option_c": "传输层", "option_d": "应用层",
            "correct_answer": "B",
            "analysis": "网络层负责分组转发和路由选择",
            "difficulty": 1, "tags": "网络体系结构",
        },
        {
            "year": 2024, "source": "示例-计算机网络",
            "question_type": "单选", "question_number": 2,
            "title": "TCP协议通过什么机制保证可靠传输？",
            "option_a": "仅校验和", "option_b": "确认和重传", "option_c": "仅流量控制", "option_d": "仅加密",
            "correct_answer": "B",
            "analysis": "TCP通过确认应答+超时重传+序号机制保证可靠传输",
            "difficulty": 1, "tags": "传输层,TCP",
        },
    ],
    "english": [
        {
            "year": 2024, "source": "示例-英语",
            "question_type": "完形", "question_number": 1,
            "title": "In recent years, artificial intelligence has ____ significant progress in various fields.",
            "option_a": "made", "option_b": "done", "option_c": "taken", "option_d": "given",
            "correct_answer": "A",
            "analysis": '"make progress"是固定搭配，表示"取得进展"',
            "difficulty": 1, "tags": "完形填空,固定搭配",
        },
        {
            "year": 2024, "source": "示例-英语",
            "question_type": "阅读", "question_number": 2,
            "title": "According to the passage, the main reason for climate change is:\\n\\nClimate change has become one of the most pressing issues of our time. Scientists have concluded that human activities, particularly the burning of fossil fuels, are the primary driver of global warming.",
            "option_a": "Natural weather cycles", "option_b": "Human activities",
            "option_c": "Solar radiation changes", "option_d": "Volcanic eruptions",
            "correct_answer": "B",
            "analysis": "文章明确指出human activities是climate change的主要原因",
            "difficulty": 2, "tags": "阅读,环境",
        },
    ],
}


def seed():
    app = create_app()
    with app.app_context():
        ExamQuestion.query.filter_by(is_public=True).delete()
        db.session.commit()

        total = 0
        for code, qs in QUESTIONS.items():
            subj = Subject.query.filter_by(code=code).first()
            if not subj:
                print(f"科目 {code} 不存在，跳过")
                continue
            for q in qs:
                db.session.add(ExamQuestion(
                    subject_id=subj.id,
                    year=q.get("year"),
                    source=q.get("source", ""),
                    question_type=q.get("question_type", "单选"),
                    question_number=q.get("question_number"),
                    title=q["title"],
                    option_a=q.get("option_a", ""),
                    option_b=q.get("option_b", ""),
                    option_c=q.get("option_c", ""),
                    option_d=q.get("option_d", ""),
                    correct_answer=q["correct_answer"],
                    analysis=q.get("analysis", ""),
                    difficulty=q.get("difficulty", 3),
                    tags=q.get("tags", ""),
                    is_public=True,
                ))
                total += 1
            print(f"  {subj.name}: {len(qs)} 题")

        db.session.commit()
        print(f"\n共写入 {total} 道公共题目")


if __name__ == "__main__":
    seed()
