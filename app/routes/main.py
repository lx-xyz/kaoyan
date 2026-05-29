import random
from datetime import datetime, timedelta, date
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from app import db
from app.models import StudySession, ExamRecord, MistakeItem, VocabularyWord, SystemSetting, Subject, get_visible_subjects, DefaultImage

main_bp = Blueprint("main", __name__)


def _exam_countdown(user):
    """计算距离考研的天数"""
    today = date.today()
    if user.exam_date:
        exam = user.exam_date
    else:
        exam = date(today.year, 12, 20)
    delta = (exam - today).days
    return delta, exam.strftime("%Y年%m月%d日")



def _get_setting(key, default=""):
    s = SystemSetting.query.filter_by(key=key).first()
    return s.value if s else default


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        from flask import redirect, url_for
        return redirect(url_for("main.dashboard"))

    from flask import session as flask_session
    show_logout_msg = flask_session.pop("show_logout_msg", False)

    images = {
        "hero": _get_setting("hero_image", ""),
    }
    if current_user.is_authenticated:
        subjects = get_visible_subjects(current_user.id).all()
    else:
        subjects = Subject.query.filter_by(is_default=True).order_by(Subject.sort_order).all()
    return render_template("index.html", images=images, subjects=subjects,
                           show_logout_msg=show_logout_msg)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_minutes = db.session.query(db.func.sum(StudySession.duration_minutes)).filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= today,
    ).scalar() or 0

    today_questions = ExamRecord.query.filter(
        ExamRecord.user_id == current_user.id,
        ExamRecord.created_at >= today,
    ).count()

    mistake_due = MistakeItem.query.filter_by(
        user_id=current_user.id, status="active"
    ).filter(MistakeItem.next_review_at <= now).count()

    vocab_due = VocabularyWord.query.filter_by(
        user_id=current_user.id, is_mastered=False
    ).filter(
        VocabularyWord.review_stage >= 0,
        VocabularyWord.next_review_at <= now,
    ).count()

    daily_quote = None
    if current_user.custom_quote and current_user.custom_quote.strip():
        lines = [l.strip() for l in current_user.custom_quote.strip().split('\n') if l.strip()]
    else:
        default_q = _get_setting("default_quote", "")
        lines = [l.strip() for l in default_q.split('\n') if l.strip()] if default_q else []
    if lines:
        day_seed = int(today.strftime("%Y%m%d"))
        random.seed(day_seed)
        daily_quote = random.choice(lines)
        random.seed()

    countdown_days, countdown_date = _exam_countdown(current_user)

    # 仪表盘图：用户自己 > 默认图库第一张
    first_dash = DefaultImage.query.filter_by(key="dashboard").first()
    dashboard_img = current_user.dashboard_img or (first_dash.url if first_dash else "")
    dash_imgs = DefaultImage.query.filter_by(key="dashboard").all()
    dash_urls = [dashboard_img] + [i.url for i in dash_imgs]
    dash_urls = [u for u in dash_urls if u]
    # 去重
    seen = set()
    unique = []
    for u in dash_urls:
        if u not in seen:
            seen.add(u); unique.append(u)
    dash_urls = unique
    if not dashboard_img and dash_urls:
        dashboard_img = dash_urls[0]

    return render_template(
        "dashboard.html",
        today_minutes=today_minutes,
        today_questions=today_questions,
        mistake_due=mistake_due,
        vocab_due=vocab_due,
        daily_quote=daily_quote,
        countdown_days=countdown_days,
        countdown_date=countdown_date,
        dashboard_img=dashboard_img,
        dash_urls=dash_urls,
    )
