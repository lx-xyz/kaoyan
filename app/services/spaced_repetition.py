"""
艾宾浩斯记忆曲线 — 间隔复习算法
错题追踪和单词记忆共用此模块
"""
from datetime import datetime, timedelta

# 各阶段的复习间隔（天数）
STAGE_INTERVALS = {
    0: 1,   # 首次错误 → 1天后复习
    1: 3,   # 第1次复习 → 3天后
    2: 7,   # 第2次复习 → 7天后
    3: 15,  # 第3次复习 → 15天后
    4: 30,  # 第4次复习 → 30天后
}

MAX_STAGE = 5  # 阶段5 = 已掌握


def get_next_review_date(stage, from_date=None):
    """根据当前阶段计算下次复习日期"""
    if from_date is None:
        from_date = datetime.utcnow()
    if stage >= MAX_STAGE:
        return None  # 已掌握，无需复习
    interval = STAGE_INTERVALS.get(stage, 1)
    return from_date + timedelta(days=interval)


def advance_stage(current_stage, result):
    """
    根据复习结果推进阶段
    result: 'correct' → 推进
            'fuzzy'   → 保持
            'wrong'   → 重置
    返回: (new_stage, next_review_date)
    """
    if result == "correct":
        new_stage = min(current_stage + 1, MAX_STAGE)
    elif result == "wrong":
        new_stage = 0
    else:  # fuzzy
        new_stage = current_stage

    next_date = get_next_review_date(new_stage)
    return new_stage, next_date


def get_due_items(query):
    """从查询中筛选到期需要复习的条目"""
    now = datetime.utcnow()
    return query.filter(
        query.column_descriptions[0]['entity'].next_review_at <= now
    )
