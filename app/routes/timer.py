import json
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import get_visible_subjects, Subject, StudySession, SystemSetting, DefaultImage, UserImage

timer_bp = Blueprint("timer", __name__)


@timer_bp.route("/timer")
@login_required
def timer_page():
    subjects = get_visible_subjects(current_user.id).all()
    # 今日学习时长
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    sessions = StudySession.query.filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= today,
    ).all()
    today_minutes = sum(s.duration_minutes for s in sessions)
    today_sessions = len(sessions)

    # 侧边图
    user_t = UserImage.query.filter_by(user_id=current_user.id, key="timer_image").all()
    admin_t = DefaultImage.query.filter_by(key="timer").all()
    first_u = user_t[0].url if user_t else ""
    first_a = admin_t[0].url if admin_t else ""
    timer_img = first_u or first_a or ""
    timer_urls = [i.url for i in user_t] + [i.url for i in admin_t]
    timer_urls = [u for u in timer_urls if u]
    seen = set()
    unique = []
    for u in timer_urls:
        if u not in seen:
            seen.add(u); unique.append(u)
    timer_urls = unique
    if not timer_img and timer_urls:
        timer_img = timer_urls[0]

    # 语录
    quote_lines = [l.strip() for l in current_user.custom_quote.split('\n') if l.strip()] if current_user.custom_quote else []
    import random as _r
    quote = _r.choice(quote_lines) if quote_lines else None

    return render_template(
        "timer/pomodoro.html",
        subjects=subjects,
        today_minutes=today_minutes,
        today_sessions=today_sessions,
        timer_img=timer_img,
        timer_urls=timer_urls,
        quote=quote,
    )


@timer_bp.route("/api/timer/record", methods=["POST"])
@login_required
def record_session():
    data = request.get_json()
    if not data:
        return jsonify({"error": "无效数据"}), 400

    subject_id = data.get("subject_id")
    duration_minutes = data.get("duration_minutes", 25)
    start_time_str = data.get("start_time")

    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
    else:
        start_time = datetime.utcnow()

    end_time = datetime.utcnow()

    session = StudySession(
        user_id=current_user.id,
        subject_id=subject_id if subject_id else None,
        start_time=start_time,
        end_time=end_time,
        duration_minutes=duration_minutes,
        session_type="pomodoro",
    )
    db.session.add(session)
    db.session.commit()

    # 今日总计
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    sessions = StudySession.query.filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= today,
    ).all()
    today_minutes = sum(s.duration_minutes for s in sessions)

    return jsonify({"ok": True, "today_minutes": today_minutes})
