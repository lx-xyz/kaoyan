from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import get_visible_subjects, Subject, StudySession, ExamRecord, VocabularyWord, MistakeItem

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile")
@login_required
def profile():
    return render_template("user/profile.html")


@user_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def profile_edit():
    if request.method == "POST":
        current_user.nickname = request.form.get("nickname", current_user.username)
        current_user.target_school = request.form.get("target_school", "")
        current_user.target_major = request.form.get("target_major", "")
        daily_goal = request.form.get("daily_goal_hours", "4")
        try:
            current_user.daily_goal_hours = int(daily_goal)
        except ValueError:
            current_user.daily_goal_hours = 4
        exam_date_str = request.form.get("exam_date", "")
        if exam_date_str:
            from datetime import datetime as dt
            try:
                current_user.exam_date = dt.strptime(exam_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        else:
            current_user.exam_date = None
        current_user.dashboard_img = request.form.get("dashboard_img", "").strip()
        current_user.timer_img = request.form.get("timer_img", "").strip()
        current_user.custom_quote = request.form.get("custom_quote", "").strip()
        db.session.commit()
        flash("个人资料已更新。", "success")
        return redirect(url_for("user.profile"))
    return render_template("user/profile_edit.html")


@user_bp.route("/stats")
@login_required
def stats():
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 今日数据
    today_sessions = StudySession.query.filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= today,
    ).all()
    today_minutes = sum(s.duration_minutes for s in today_sessions)

    # 今日做题
    today_questions = ExamRecord.query.filter(
        ExamRecord.user_id == current_user.id,
        ExamRecord.created_at >= today,
    ).count()

    # 总数据
    total_minutes = db.session.query(db.func.sum(StudySession.duration_minutes)).filter_by(
        user_id=current_user.id
    ).scalar() or 0
    total_questions = ExamRecord.query.filter_by(user_id=current_user.id).count()
    total_words = VocabularyWord.query.filter_by(user_id=current_user.id).count()
    mastered_words = VocabularyWord.query.filter_by(user_id=current_user.id, is_mastered=True).count()
    mistake_count = MistakeItem.query.filter_by(user_id=current_user.id, status="active").count()
    study_days = db.session.query(db.func.count(
        db.func.distinct(db.func.date(StudySession.start_time))
    )).filter_by(user_id=current_user.id).scalar() or 0

    # 近7天每日学习时长
    daily_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = day
        day_end = day + timedelta(days=1)
        minutes = db.session.query(db.func.sum(StudySession.duration_minutes)).filter(
            StudySession.user_id == current_user.id,
            StudySession.start_time >= day_start,
            StudySession.start_time < day_end,
        ).scalar() or 0
        daily_data.append({
            "date": day.strftime("%m/%d"),
            "minutes": minutes,
        })

    # 各科目学习时间
    subjects = get_visible_subjects(current_user.id).all()
    subject_data = []
    for s in subjects:
        mins = db.session.query(db.func.sum(StudySession.duration_minutes)).filter(
            StudySession.user_id == current_user.id,
            StudySession.subject_id == s.id,
        ).scalar() or 0
        if mins > 0:
            subject_data.append({"name": s.name, "minutes": mins, "color": s.color})

    return render_template(
        "user/stats.html",
        today_minutes=today_minutes,
        today_questions=today_questions,
        total_minutes=total_minutes,
        total_questions=total_questions,
        total_words=total_words,
        mastered_words=mastered_words,
        mistake_count=mistake_count,
        study_days=study_days,
        daily_data=daily_data,
        subject_data=subject_data,
    )
