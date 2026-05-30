import os
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Subject, SystemSetting, DefaultImage, ExamQuestion, VocabularyWord

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash("需要管理员权限。", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


def _get_setting(key, default=""):
    s = SystemSetting.query.filter_by(key=key).first()
    return s.value if s else default


def _save_setting(key, value):
    s = SystemSetting.query.filter_by(key=key).first()
    if s:
        s.value = value
    else:
        db.session.add(SystemSetting(key=key, value=value))
    db.session.commit()


@admin_bp.route("/")
@admin_required
def index():
    hero_img = _get_setting("hero_image", "")
    dashboard_img = _get_setting("dashboard_image", "")
    timer_img = _get_setting("timer_image", "")
    default_quote = _get_setting("default_quote", "")
    default_subjects = Subject.query.filter_by(is_default=True).order_by(Subject.sort_order).all()
    default_imgs = DefaultImage.query.all()
    public_q_count = ExamQuestion.query.filter_by(is_public=True).count()

    from app.models import HiddenSubject
    hidden_ids = [h.subject_id for h in HiddenSubject.query.filter_by(user_id=current_user.id).all()]
    from sqlalchemy import or_
    q = Subject.query.filter(
        or_(Subject.is_default == True, Subject.user_id == current_user.id)
    )
    if hidden_ids:
        q = q.filter(~Subject.id.in_(hidden_ids))
    my_subjects = q.order_by(Subject.sort_order).all()

    return render_template("admin/index.html",
        hero_img=hero_img, dashboard_img=dashboard_img, timer_img=timer_img,
        default_quote=default_quote,
        default_subjects=default_subjects,
        default_imgs=default_imgs,
        public_q_count=public_q_count,
        my_subjects=my_subjects,
    )


# ===== 主图保存（Hero/仪表盘/计时） =====
@admin_bp.route("/save-images", methods=["POST"])
@admin_required
def save_images():
    _save_setting("hero_image", request.form.get("hero_url", "").strip())
    _save_setting("dashboard_image", request.form.get("dash_url", "").strip())
    _save_setting("timer_image", request.form.get("timer_url", "").strip())
    flash("图片设置已保存。", "success")
    return redirect(url_for("admin.index"))


# ===== 管理员自己的科目 =====
@admin_bp.route("/my-subjects", methods=["POST"])
@admin_required
def my_subjects():
    action = request.form.get("action")
    name = request.form.get("name", "").strip()
    sid = request.form.get("id", type=int)
    if action == "add" and name:
        code = request.form.get("code", "").strip() or name.lower()
        color = request.form.get("color", "#E8A817")
        db.session.add(Subject(name=name, code=code, color=color,
                               sort_order=Subject.query.count()+1, user_id=current_user.id))
        db.session.commit()
        flash(f"科目「{name}」已添加。", "success")
    elif action == "delete" and sid:
        s = Subject.query.get(sid)
        if s and s.is_default:
            from app.models import HiddenSubject
            if not HiddenSubject.query.filter_by(user_id=current_user.id, subject_id=s.id).first():
                db.session.add(HiddenSubject(user_id=current_user.id, subject_id=s.id))
                db.session.commit()
                flash(f"默认科目「{s.name}」已隐藏。", "info")
        elif s and s.user_id == current_user.id:
            db.session.delete(s)
            db.session.commit()
            flash(f"科目「{s.name}」已删除。", "info")
    return redirect(url_for("admin.index"))


# ===== Hero图 =====
@admin_bp.route("/hero", methods=["POST"])
@admin_required
def hero_upload():
    file = request.files.get("file")
    url_input = request.form.get("url", "").strip()
    if url_input:
        _save_setting("hero_image", url_input)
        flash("Hero图已更新。", "success")
    elif file and file.filename:
        filename = f"hero_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
        d = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(d, exist_ok=True)
        try:
            from PIL import Image as PILImage
            img = PILImage.open(file)
            if img.mode in ('RGBA','P'): img = img.convert('RGB')
            img.save(os.path.join(d, filename), 'JPEG', quality=85)
        except:
            file.save(os.path.join(d, filename))
        _save_setting("hero_image", f"/static/uploads/{filename}")
        flash("Hero图已上传。", "success")
    return redirect(url_for("admin.index"))


# ===== 默认图库 =====
@admin_bp.route("/default-images", methods=["POST"])
@admin_required
def default_images():
    action = request.form.get("action")
    if action == "add":
        key = request.form.get("key", "dashboard")
        file = request.files.get("file")
        url_input = request.form.get("url", "").strip()
        img_url = url_input
        if file and file.filename:
            filename = f"dimg_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
            d = os.path.join(current_app.root_path, "static", "uploads")
            os.makedirs(d, exist_ok=True)
            try:
                from PIL import Image as PILImage
                img = PILImage.open(file)
                if img.mode in ('RGBA','P'): img = img.convert('RGB')
                img.save(os.path.join(d, filename), 'JPEG', quality=85)
            except:
                file.save(os.path.join(d, filename))
            img_url = f"/static/uploads/{filename}"
        if img_url:
            db.session.add(DefaultImage(key=key, url=img_url))
            db.session.commit()
            flash("默认图已添加。", "success")
    elif action == "delete":
        img_id = request.form.get("id", type=int)
        img = DefaultImage.query.get(img_id)
        if img:
            db.session.delete(img)
            db.session.commit()
            flash("默认图已删除。", "info")
    return redirect(url_for("admin.index"))


# ===== 默认语录 =====
@admin_bp.route("/quote", methods=["POST"])
@admin_required
def quote():
    text = request.form.get("quote", "").strip()
    _save_setting("default_quote", text)
    flash("默认语录已保存。", "success")
    return redirect(url_for("admin.index"))


# ===== 科目管理 =====
@admin_bp.route("/subjects", methods=["POST"])
@admin_required
def subjects():
    action = request.form.get("action")
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip()
    color = request.form.get("color", "#E8A817")
    sid = request.form.get("id", type=int)

    if action == "add" and name:
        s = Subject(name=name, code=code or name.lower(), color=color,
                    sort_order=Subject.query.count() + 1,
                    is_default=True, user_id=None)
        db.session.add(s)
        db.session.commit()
        flash(f"默认科目「{name}」已添加。", "success")
    elif action == "delete" and sid:
        s = Subject.query.get(sid)
        if s and s.is_default:
            db.session.delete(s)
            db.session.commit()
            flash(f"默认科目「{s.name}」已删除。", "info")
    return redirect(url_for("admin.index"))
