import random
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import VocabularyWord
from app.services.spaced_repetition import advance_stage

vocab_bp = Blueprint("vocab", __name__)

# 阶段说明：
#   -1 = 新词未学（刚添加，没有进入复习周期）
#   0~4 = 复习中（间隔：1天→3天→7天→15天→30天）
#   5 = 已掌握


def _counts():
    """返回当前用户的单词统计"""
    now = datetime.utcnow()
    base = VocabularyWord.query.filter_by(user_id=current_user.id)
    return {
        "total": base.count(),
        "new": base.filter_by(review_stage=-1).count(),
        "due": base.filter(
            VocabularyWord.review_stage >= 0,
            VocabularyWord.review_stage < 5,
            VocabularyWord.is_mastered == False,
            VocabularyWord.next_review_at <= now,
        ).count(),
        "learning": base.filter(
            VocabularyWord.review_stage >= 0, VocabularyWord.review_stage < 5,
            VocabularyWord.is_mastered == False,
        ).count(),
        "mastered": base.filter_by(is_mastered=True).count(),
    }


# ---- 单词列表（浏览模式）----
@vocab_bp.route("/vocab")
@login_required
def list_words():
    stage_filter = request.args.get("stage", "")
    search = request.args.get("search", "").strip()

    query = VocabularyWord.query.filter_by(user_id=current_user.id)

    if stage_filter == "new":
        query = query.filter_by(review_stage=-1)
    elif stage_filter == "learning":
        query = query.filter(
            VocabularyWord.review_stage >= 0, VocabularyWord.review_stage < 5,
            VocabularyWord.is_mastered == False,
        )
    elif stage_filter == "due":
        now = datetime.utcnow()
        query = query.filter(
            VocabularyWord.review_stage >= 0, VocabularyWord.review_stage < 5,
            VocabularyWord.is_mastered == False,
            VocabularyWord.next_review_at <= now,
        )
    elif stage_filter == "mastered":
        query = query.filter_by(is_mastered=True)

    if search:
        query = query.filter(
            VocabularyWord.word.contains(search) |
            VocabularyWord.meaning.contains(search)
        )

    query = query.order_by(VocabularyWord.created_at.desc())
    words = query.all()

    counts = _counts()

    return render_template(
        "vocab/list.html",
        words=words, counts=counts,
        current_stage=stage_filter, search=search,
        now=datetime.utcnow(),
    )


# ---- 添加单词 ----
@vocab_bp.route("/vocab/add", methods=["GET", "POST"])
@login_required
def add_word():
    if request.method == "POST":
        text = request.form.get("words_text", "").strip()
        if not text:
            flash("请输入单词。", "warning")
            return render_template("vocab/add.html")

        lines = text.strip().split("\n")
        added = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split("|")]
            word_text = parts[0] if len(parts) >= 1 else ""
            meaning = parts[1] if len(parts) >= 2 else ""
            phonetic = parts[2] if len(parts) >= 3 else ""

            if not word_text:
                continue

            existing = VocabularyWord.query.filter_by(
                user_id=current_user.id, word=word_text
            ).first()
            if existing:
                continue

            # 新词 stage=-1，不设 next_review_at（未进入复习周期）
            word = VocabularyWord(
                user_id=current_user.id,
                word=word_text,
                phonetic=phonetic,
                meaning=meaning,
                review_stage=-1,
            )
            db.session.add(word)
            added += 1

        db.session.commit()
        if added:
            flash(f"成功添加 {added} 个新词！", "success")
        else:
            flash("没有新词可添加（可能已存在或格式错误）。", "warning")
        return redirect(url_for("vocab.list_words"))

    return render_template("vocab/add.html")


# ---- 学习新词（会话多轮机制）----
@vocab_bp.route("/vocab/learn")
@login_required
def learn():
    """学习新词 — 每轮N个词，不认识的轮完再来"""
    from flask import session as flask_session

    count = request.args.get("count", type=int) or flask_session.get("learn_count") or 10
    pool = flask_session.get("learn_pool", [])
    retry = flask_session.get("learn_retry", [])

    # 用户自选词 / 从新词池随机取
    selected = request.args.get("ids", "")
    if not pool:
        if selected:
            # 用户从列表页勾选的词
            ids = [int(x) for x in selected.split(",") if x.strip().isdigit()]
            new_words = VocabularyWord.query.filter(
                VocabularyWord.user_id == current_user.id,
                VocabularyWord.id.in_(ids),
                VocabularyWord.review_stage == -1,
            ).all()
        else:
            # 随机取N个新词
            new_words = VocabularyWord.query.filter_by(
                user_id=current_user.id, review_stage=-1
            ).order_by(db.func.random()).limit(count).all()

        if not new_words and not retry:
            return render_template("vocab/learn_empty.html", counts=_counts())

        if new_words:
            pool = [w.id for w in new_words]
        retry = []
        flask_session["learn_pool"] = pool
        flask_session["learn_retry"] = retry
        flask_session["learn_count"] = count

    # 当前要展示的词：优先从 pool 取（还没轮到的），pool 空了从 retry 取
    if pool:
        current_id = pool.pop(0)
    elif retry:
        # 本轮结束，不认识的词进入下一轮
        pool = list(retry)
        retry = []
        current_id = pool.pop(0)
        flash(f"本轮结束！{len(pool) + 1} 个词再来一遍。", "warning")
    else:
        # 全部学完
        flask_session.pop("learn_pool", None)
        flask_session.pop("learn_retry", None)
        return render_template("vocab/learn_empty.html", counts=_counts())

    flask_session["learn_pool"] = pool
    flask_session["learn_retry"] = retry

    word = VocabularyWord.query.get(current_id)
    if not word:
        return redirect(url_for("vocab.learn"))

    # 本轮进度
    total_new = VocabularyWord.query.filter_by(
        user_id=current_user.id, review_stage=-1
    ).count()
    learned_this_session = VocabularyWord.query.filter(
        VocabularyWord.user_id == current_user.id,
        VocabularyWord.review_stage >= 0,
    ).count()

    return render_template(
        "vocab/learn.html",
        word=word,
        counts=_counts(),
        pool_count=len(pool),
        retry_count=len(retry),
        total_new=total_new,
        count=count,
    )


@vocab_bp.route("/vocab/<int:word_id>/learn", methods=["POST"])
@login_required
def learn_action(word_id):
    from flask import session as flask_session

    word = VocabularyWord.query.get_or_404(word_id)
    if word.user_id != current_user.id:
        flash("无权操作。", "danger")
        return redirect(url_for("vocab.learn"))

    result = request.form.get("result", "wrong")
    retry = flask_session.get("learn_retry", [])
    from datetime import timedelta

    # 认识：1天后复习；不认识：10分钟后复习
    word.review_stage = 0
    word.review_count = 0
    word.is_mastered = False

    if result == "correct":
        word.next_review_at = datetime.utcnow() + timedelta(days=1)
        db.session.commit()
        flash(f'"{word.word}" → 认识！明天复习。', "success")
    else:
        word.next_review_at = datetime.utcnow() + timedelta(minutes=10)
        retry.append(word.id)
        flask_session["learn_retry"] = retry
        db.session.commit()
        flash(f'"{word.word}" → {word.meaning}', "info")

    return redirect(url_for("vocab.learn"))


# ---- 复习（选择题模式）----
@vocab_bp.route("/vocab/review")
@login_required
def review():
    """复习 — 选择题模式：显示单词+4个选项"""
    now = datetime.utcnow()

    # 优先取到期的复习词（stage 0-4）
    word = VocabularyWord.query.filter(
        VocabularyWord.user_id == current_user.id,
        VocabularyWord.review_stage >= 0,
        VocabularyWord.review_stage < 5,
        VocabularyWord.is_mastered == False,
        VocabularyWord.next_review_at <= now,
    ).order_by(VocabularyWord.next_review_at.asc()).first()

    if not word:
        counts = _counts()
        return render_template("vocab/review_empty.html", counts=counts)

    # 生成4个选项（1个正确 + 3个干扰项）
    distractors = VocabularyWord.query.filter(
        VocabularyWord.user_id == current_user.id,
        VocabularyWord.id != word.id,
    ).order_by(db.func.random()).limit(3).all()

    options = [word.meaning]
    for d in distractors:
        options.append(d.meaning)
    random.shuffle(options)

    correct_index = options.index(word.meaning)
    labels = ["A", "B", "C", "D"]

    return render_template(
        "vocab/review.html",
        word=word,
        options=options,
        labels=labels,
        correct_label=labels[correct_index],
        counts=_counts(),
    )


@vocab_bp.route("/vocab/<int:word_id>/review", methods=["POST"])
@login_required
def review_action(word_id):
    word = VocabularyWord.query.get_or_404(word_id)
    if word.user_id != current_user.id:
        return jsonify({"error": "无权操作"}), 403

    review_result = request.form.get("result", "wrong")
    is_correct = (review_result == "correct")
    new_stage, next_date = advance_stage(word.review_stage, review_result)

    word.review_stage = new_stage
    word.next_review_at = next_date if next_date else datetime.utcnow()
    word.last_review_at = datetime.utcnow()
    word.review_count += 1

    if new_stage >= 5:
        word.is_mastered = True
    elif not is_correct:
        word.is_mastered = False

    db.session.commit()

    return render_template(
        "vocab/review_result.html",
        word=word,
        is_correct=is_correct,
    )


# ---- 卡片模式（翻转记忆）----
@vocab_bp.route("/vocab/cards")
@login_required
def cards():
    """卡片翻转模式 — 查看所有单词的卡片"""
    words = VocabularyWord.query.filter_by(
        user_id=current_user.id
    ).order_by(VocabularyWord.created_at.desc()).all()
    return render_template("vocab/cards.html", words=words, counts=_counts())


# ---- 操作 ----
@vocab_bp.route("/vocab/<int:word_id>/toggle", methods=["POST"])
@login_required
def toggle_word(word_id):
    word = VocabularyWord.query.get_or_404(word_id)
    if word.user_id != current_user.id:
        flash("无权操作。", "danger")
        return redirect(url_for("vocab.list_words"))
    if word.is_mastered:
        word.is_mastered = False
        word.review_stage = 0
        word.next_review_at = datetime.utcnow()
    else:
        word.is_mastered = True
        word.review_stage = 5
    db.session.commit()
    return redirect(url_for("vocab.list_words"))


@vocab_bp.route("/vocab/<int:word_id>/delete", methods=["POST"])
@login_required
def delete_word(word_id):
    word = VocabularyWord.query.get_or_404(word_id)
    if word.user_id != current_user.id:
        flash("无权操作。", "danger")
        return redirect(url_for("vocab.list_words"))
    db.session.delete(word)
    db.session.commit()
    flash("单词已删除。", "info")
    return redirect(url_for("vocab.list_words"))


@vocab_bp.route("/vocab/<int:word_id>/reset", methods=["POST"])
@login_required
def reset_word(word_id):
    """重置为新词状态"""
    word = VocabularyWord.query.get_or_404(word_id)
    if word.user_id != current_user.id:
        flash("无权操作。", "danger")
        return redirect(url_for("vocab.list_words"))
    word.review_stage = -1
    word.next_review_at = None
    word.review_count = 0
    word.is_mastered = False
    db.session.commit()
    flash("已重置为新词。", "info")
    return redirect(url_for("vocab.list_words"))
