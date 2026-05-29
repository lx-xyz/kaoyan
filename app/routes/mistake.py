from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import get_visible_subjects, Subject, MistakeItem, ExamRecord
from app.services.spaced_repetition import advance_stage

mistake_bp = Blueprint("mistake", __name__)


@mistake_bp.route("/mistake")
@login_required
def list_mistakes():
    subject_filter = request.args.get("subject", type=int)
    status_filter = request.args.get("status", "active")

    query = MistakeItem.query.filter_by(user_id=current_user.id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    if subject_filter:
        query = query.join(MistakeItem.question).filter(
            MistakeItem.question.has(subject_id=subject_filter)
        )

    query = query.order_by(MistakeItem.last_wrong_at.desc())
    mistakes = query.all()

    # 统计待复习数量
    now = datetime.utcnow()
    due_count = MistakeItem.query.filter_by(
        user_id=current_user.id, status="active"
    ).filter(
        MistakeItem.next_review_at <= now
    ).count()

    subjects = get_visible_subjects(current_user.id).all()

    return render_template(
        "mistake/list.html",
        mistakes=mistakes,
        due_count=due_count,
        subjects=subjects,
        current_subject=subject_filter,
        current_status=status_filter,
        now=datetime.utcnow(),
    )


@mistake_bp.route("/mistake/review", methods=["GET", "POST"])
@login_required
def review():
    """错题复习 — 按记忆曲线出题"""
    mistake_id = request.args.get("mid", type=int)

    # 取到期待复习的错题
    now = datetime.utcnow()
    query = MistakeItem.query.filter_by(user_id=current_user.id, status="active")
    if mistake_id:
        query = query.filter_by(id=mistake_id)
    else:
        query = query.filter(MistakeItem.next_review_at <= now)

    item = query.order_by(MistakeItem.next_review_at.asc()).first()

    if not item:
        total_active = MistakeItem.query.filter_by(
            user_id=current_user.id, status="active"
        ).count()
        return render_template("mistake/review_empty.html", total_active=total_active)

    question = item.question
    result = None

    if request.method == "POST":
        user_answer = request.form.get("answer", "").strip()
        correct_answer = question.correct_answer.strip().upper()
        is_correct = (user_answer.strip().upper() == correct_answer)

        # 记录做题
        record = ExamRecord(
            user_id=current_user.id,
            question_id=question.id,
            user_answer=user_answer,
            is_correct=is_correct,
            session_type="review",
        )
        db.session.add(record)

        # 更新错题状态
        review_result = "correct" if is_correct else "wrong"
        new_stage, next_date = advance_stage(item.mastery_level, review_result)

        item.mastery_level = new_stage
        item.next_review_at = next_date
        item.last_review_at = datetime.utcnow()
        if is_correct and new_stage >= 5:
            item.status = "mastered"
        if not is_correct:
            item.wrong_count += 1
            item.last_wrong_at = datetime.utcnow()

        db.session.commit()

        result = {
            "is_correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": question.correct_answer,
            "item": item,
        }

    return render_template(
        "mistake/review.html",
        item=item,
        question=question,
        result=result,
    )


@mistake_bp.route("/mistake/<int:item_id>/toggle", methods=["POST"])
@login_required
def toggle_status(item_id):
    item = MistakeItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash("无权操作。", "danger")
        return redirect(url_for("mistake.list_mistakes"))
    if item.status == "active":
        item.status = "mastered"
        flash("已标记为掌握。", "info")
    else:
        item.status = "active"
        flash("已移回待复习。", "info")
    db.session.commit()
    return redirect(url_for("mistake.list_mistakes"))
