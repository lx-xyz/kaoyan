from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import get_visible_subjects, Note, Subject

note_bp = Blueprint("note", __name__)


@note_bp.route("/note")
@login_required
def list_notes():
    subject_filter = request.args.get("subject", type=int)
    query = Note.query.filter_by(user_id=current_user.id)

    if subject_filter:
        query = query.filter_by(subject_id=subject_filter)

    query = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
    notes = query.all()
    subjects = get_visible_subjects(current_user.id).all()

    return render_template(
        "note/list.html",
        notes=notes,
        subjects=subjects,
        current_subject=subject_filter,
    )


@note_bp.route("/note/create", methods=["GET", "POST"])
@login_required
def create_note():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        subject_id = request.form.get("subject_id", type=int)
        category = request.form.get("category", "").strip()

        if not title:
            flash("请输入笔记标题。", "warning")
            subjects = get_visible_subjects(current_user.id).all()
            return render_template("note/edit.html", note=None, subjects=subjects)

        note = Note(
            user_id=current_user.id,
            title=title,
            content=content,
            subject_id=subject_id if subject_id else None,
            category=category,
        )
        db.session.add(note)
        db.session.commit()
        flash("笔记已保存。", "success")
        return redirect(url_for("note.list_notes"))

    subjects = get_visible_subjects(current_user.id).all()
    return render_template("note/edit.html", note=None, subjects=subjects)


@note_bp.route("/note/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("无权操作。", "danger")
        return redirect(url_for("note.list_notes"))

    if request.method == "POST":
        note.title = request.form.get("title", "").strip()
        note.content = request.form.get("content", "").strip()
        note.subject_id = request.form.get("subject_id", type=int)
        note.category = request.form.get("category", "").strip()
        note.updated_at = datetime.utcnow()
        db.session.commit()
        flash("笔记已更新。", "success")
        return redirect(url_for("note.list_notes"))

    subjects = get_visible_subjects(current_user.id).all()
    return render_template("note/edit.html", note=note, subjects=subjects)


@note_bp.route("/note/<int:note_id>/toggle-pin", methods=["POST"])
@login_required
def toggle_pin(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("无权操作。", "danger")
        return redirect(url_for("note.list_notes"))
    note.is_pinned = not note.is_pinned
    db.session.commit()
    return redirect(url_for("note.list_notes"))


@note_bp.route("/note/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("无权操作。", "danger")
        return redirect(url_for("note.list_notes"))
    db.session.delete(note)
    db.session.commit()
    flash("笔记已删除。", "info")
    return redirect(url_for("note.list_notes"))
