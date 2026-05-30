import os
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.models import SystemSetting, UserImage, Subject

settings_bp = Blueprint("settings", __name__)

# 首页可自定义的图片key及其默认值
IMAGE_KEYS = {
    "dashboard_image": "",
    "timer_image": "",
}

IMAGE_LABELS = {
    "dashboard_image": "仪表盘侧边图",
    "timer_image": "计时页侧边图",
}


def get_setting(key, default=""):
    s = SystemSetting.query.filter_by(key=key).first()
    return s.value if s else default


@settings_bp.route("/settings")
@login_required
def page():
    images = {}
    for key, default in IMAGE_KEYS.items():
        user_imgs = UserImage.query.filter_by(user_id=current_user.id, key=key).all()
        images[key] = {
            "value": user_imgs[0].url if user_imgs else get_setting(key, default),
            "label": IMAGE_LABELS.get(key, key),
            "user_imgs": user_imgs,
        }
    # 科目：默认 + 自己创建的，去掉隐藏的
    from app.models import HiddenSubject
    hidden_ids = [h.subject_id for h in HiddenSubject.query.filter_by(user_id=current_user.id).all()]
    from sqlalchemy import or_
    q = Subject.query.filter(
        or_(Subject.is_default == True, Subject.user_id == current_user.id)
    )
    if hidden_ids:
        q = q.filter(~Subject.id.in_(hidden_ids))
    subjects = q.order_by(Subject.sort_order).all()

    return render_template("settings/index.html", images=images, subjects=subjects)


@settings_bp.route("/settings/upload", methods=["POST"])
@login_required
def upload():
    key = request.form.get("key")
    if key not in IMAGE_KEYS:
        flash("无效的设置项。", "danger")
        return redirect(url_for("settings.page"))

    url_input = request.form.get("url", "").strip()
    if url_input:
        _set_user_img(key, url_input)
        flash(f"{IMAGE_LABELS.get(key, key)} 已更新。", "success")
        return redirect(url_for("settings.page"))

    file = request.files.get("file")
    if not file or not file.filename:
        flash("请选择图片或输入URL。", "warning")
        return redirect(url_for("settings.page"))

    filename = f"setting_{key}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    upload_dir = os.path.join(current_app.root_path, "static", "uploads", "settings")
    os.makedirs(upload_dir, exist_ok=True)
    try:
        from PIL import Image as PILImage
        img = PILImage.open(file)
        if img.mode in ('RGBA','P'): img = img.convert('RGB')
        img.save(os.path.join(upload_dir, f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"), 'JPEG', quality=85)
    except:
        file.save(os.path.join(upload_dir, filename))
    _set_user_img(key, f"/static/uploads/{filename}")
    flash(f"{IMAGE_LABELS.get(key, key)} 已上传。", "success")
    return redirect(url_for("settings.page"))


def _set_user_img(key, value):
    from app.models import UserImage
    db.session.add(UserImage(user_id=current_user.id, key=key, url=value))
    db.session.commit()


@settings_bp.route("/settings/reset", methods=["POST"])
@login_required
def reset():
    key = request.form.get("key")
    if key == "dashboard_image":
        current_user.dashboard_img = ""
    elif key == "timer_image":
        current_user.timer_img = ""
    db.session.commit()
    flash(f"{IMAGE_LABELS.get(key, key)} 已恢复默认。", "info")
    return redirect(url_for("settings.page"))


def _save_setting(key, value):
    s = SystemSetting.query.filter_by(key=key).first()
    if s:
        s.value = value
    else:
        db.session.add(SystemSetting(key=key, value=value))
    db.session.commit()


@settings_bp.route("/settings/subjects", methods=["POST"])
@login_required
def manage_subjects():
    action = request.form.get("action")
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip()
    color = request.form.get("color", "#E8A817")
    subject_id = request.form.get("id", type=int)

    if action == "add" and name:
        sort = Subject.query.count()
        db.session.add(Subject(name=name, code=code or name.lower(), color=color,
                               sort_order=sort + 1, user_id=current_user.id))
        db.session.commit()
        flash(f"科目「{name}」已添加。", "success")
    elif action == "delete" and subject_id:
        s = Subject.query.get(subject_id)
        if s and s.is_default:
            # 默认科目不能真删，隐藏
            from app.models import HiddenSubject
            if not HiddenSubject.query.filter_by(user_id=current_user.id, subject_id=s.id).first():
                db.session.add(HiddenSubject(user_id=current_user.id, subject_id=s.id))
                db.session.commit()
                flash(f"默认科目「{s.name}」已隐藏。", "info")
        elif s and s.user_id == current_user.id:
            db.session.delete(s)
            db.session.commit()
            flash(f"科目「{s.name}」已删除。", "info")

    return redirect(url_for("settings.page"))
