from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("用户名或密码错误，请重试。", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember.data)
        user.last_login = datetime.utcnow()
        db.session.commit()

        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=f"{form.username.data}@user.local",
            nickname=form.username.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("注册成功！欢迎加入考研学习系统。", "success")
        login_user(user)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/guest")
def guest_login():
    import uuid
    guest_name = f"游客{str(uuid.uuid4())[:6]}"
    user = User(
        username=guest_name,
        email=f"{guest_name}@guest.local",
        nickname="游客",
        is_guest=True,
    )
    user.set_password("guest")
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=False)
    return redirect(url_for("main.dashboard"))


@auth_bp.route("/logout")
@login_required
def logout():
    is_guest = current_user.is_guest
    logout_user()
    if not is_guest:
        from flask import session
        session["show_logout_msg"] = True
    return redirect(url_for("main.index"))
