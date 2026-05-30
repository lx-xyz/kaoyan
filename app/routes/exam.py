import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import get_visible_subjects, Subject, ExamQuestion, ExamRecord, MistakeItem
from app.forms import QuestionForm

exam_bp = Blueprint("exam", __name__)


def _populate_subject_choices(form):
    subjects = get_visible_subjects(current_user.id).all()
    form.subject_id.choices = [(s.id, s.name) for s in subjects]


@exam_bp.route("/exam")
@login_required
def list_questions():
    page = request.args.get("page", 1, type=int)
    subject_filter = request.args.get("subject", type=int)
    year_filter = request.args.get("year", type=int)
    qtype_filter = request.args.get("type", "")

    query = ExamQuestion.query.filter_by(created_by=current_user.id)

    if subject_filter:
        query = query.filter_by(subject_id=subject_filter)
    if year_filter:
        query = query.filter_by(year=year_filter)
    if qtype_filter:
        query = query.filter_by(question_type=qtype_filter)

    query = query.order_by(ExamQuestion.created_at.desc())
    pagination = query.paginate(page=page, per_page=20, error_out=False)

    subjects = get_visible_subjects(current_user.id).all()
    years = db.session.query(ExamQuestion.year).filter(
        ExamQuestion.year.isnot(None)
    ).distinct().order_by(ExamQuestion.year.desc()).all()
    years = [y[0] for y in years]

    return render_template(
        "exam/list.html",
        questions=pagination.items,
        pagination=pagination,
        subjects=subjects,
        years=years,
        current_subject=subject_filter,
        current_year=year_filter,
        current_type=qtype_filter,
    )


@exam_bp.route("/exam/create", methods=["GET", "POST"])
@login_required
def create_question():
    form = QuestionForm()
    _populate_subject_choices(form)
    subject_codes = {s.id: s.code for s in get_visible_subjects(current_user.id).all()}
    if form.validate_on_submit():
        question = ExamQuestion(
            subject_id=form.subject_id.data,
            year=form.year.data,
            source=form.source.data or "",
            question_type=form.question_type.data,
            question_number=form.question_number.data,
            title=form.title.data,
            option_a=form.option_a.data or "",
            option_b=form.option_b.data or "",
            option_c=form.option_c.data or "",
            option_d=form.option_d.data or "",
            correct_answer=form.correct_answer.data,
            analysis=form.analysis.data or "",
            difficulty=form.difficulty.data or 3,
            tags=form.tags.data or "",
            created_by=current_user.id,
        )
        db.session.add(question)
        db.session.commit()
        flash("题目录入成功！", "success")
        return redirect(url_for("exam.list_questions"))
    return render_template("exam/create.html", form=form, subject_codes=subject_codes)


@exam_bp.route("/exam/<int:question_id>")
@login_required
def question_detail(question_id):
    question = ExamQuestion.query.get_or_404(question_id)
    return render_template("exam/detail.html", question=question)


@exam_bp.route("/exam/<int:question_id>/edit", methods=["GET", "POST"])
@login_required
def edit_question(question_id):
    question = ExamQuestion.query.get_or_404(question_id)
    form = QuestionForm(obj=question)
    _populate_subject_choices(form)
    if form.validate_on_submit():
        form.populate_obj(question)
        question.updated_at = datetime.utcnow()
        db.session.commit()
        flash("题目已更新。", "success")
        return redirect(url_for("exam.question_detail", question_id=question.id))
    return render_template("exam/edit.html", form=form, question=question)


@exam_bp.route("/exam/<int:question_id>/delete", methods=["POST"])
@login_required
def delete_question(question_id):
    question = ExamQuestion.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("题目已删除。", "info")
    return redirect(url_for("exam.list_questions"))


@exam_bp.route("/upload/image", methods=["POST"])
@login_required
def upload_image():
    from flask import jsonify
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "未收到图片"}), 400
    import os as _os
    from PIL import Image as PILImage
    upload_dir = current_app.config['UPLOAD_FOLDER']
    _os.makedirs(upload_dir, exist_ok=True)
    name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
    path = _os.path.join(upload_dir, name)
    try:
        img = PILImage.open(file)
        if img.mode in ('RGBA', 'P'): img = img.convert('RGB')
        img.save(path, 'JPEG', quality=85)
    except:
        file.save(path)
    url = f"/uploads/{name}"
    return jsonify({"url": url})


# ============================================================
# 做题功能
# ============================================================
def _next_practice_question(subject_id=None, qtype=None):
    """获取下一道要做的题目（随机顺序）"""
    from sqlalchemy.sql.expression import func
    query = ExamQuestion.query.filter_by(created_by=current_user.id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if qtype:
        query = query.filter_by(question_type=qtype)
    return query.order_by(func.random()).first()


def _judge_answer(question, user_answer):
    """判断答案是否正确"""
    correct = question.correct_answer.strip().upper()
    user = user_answer.strip().upper()
    if question.question_type in ("单选", "多选", "完形"):
        return user == correct
    # 填空/解答：模糊匹配（忽略空格和大小写）
    return user == correct


def _record_mistake(question):
    """记录或更新错题"""
    existing = MistakeItem.query.filter_by(
        user_id=current_user.id, question_id=question.id
    ).first()
    if existing:
        existing.wrong_count += 1
        existing.last_wrong_at = datetime.utcnow()
        existing.next_review_at = datetime.utcnow() + timedelta(minutes=10)
        existing.mastery_level = max(0, existing.mastery_level - 1)
        existing.status = "active"
    else:
        item = MistakeItem(
            user_id=current_user.id,
            question_id=question.id,
            wrong_count=1,
            last_wrong_at=datetime.utcnow(),
            next_review_at=datetime.utcnow() + timedelta(minutes=10),
            mastery_level=0,
            status="active",
        )
        db.session.add(item)


@exam_bp.route("/exam/practice", methods=["GET", "POST"])
@login_required
def practice():
    """做题主页：选题 + 提交答案"""
    subject_id = request.args.get("subject", type=int)
    qtype = request.args.get("type", "")
    question_id = request.args.get("qid", type=int)
    mode = request.args.get("mode", "random")

    question = None
    if question_id:
        question = ExamQuestion.query.get(question_id)
    if not question and mode != "browse":
        question = _next_practice_question(subject_id, qtype)

    all_questions = []
    if mode == "browse":
        q = ExamQuestion.query.filter_by(created_by=current_user.id)
        if subject_id:
            q = q.filter_by(subject_id=subject_id)
        all_questions = q.order_by(ExamQuestion.created_at.desc()).limit(50).all()

    if not question and mode != "browse":
        subjects = get_visible_subjects(current_user.id).all()
        return render_template("exam/practice_empty.html", subjects=subjects)

    result = None

    if request.method == "POST":
        posted_qid = request.form.get("question_id", type=int)
        if posted_qid and posted_qid != question.id:
            question = ExamQuestion.query.get(posted_qid)
        user_answer = request.form.get("answer", "").strip()
        is_correct = _judge_answer(question, user_answer)
        record = ExamRecord(
            user_id=current_user.id, question_id=question.id,
            user_answer=user_answer, is_correct=is_correct, session_type="practice",
        )
        db.session.add(record)
        if not is_correct:
            _record_mistake(question)
        db.session.commit()
        result = {"is_correct": is_correct, "user_answer": user_answer, "correct_answer": question.correct_answer}

    subjects = get_visible_subjects(current_user.id).all()
    return render_template(
        "exam/practice.html", question=question, result=result,
        subjects=subjects, current_subject=subject_id, current_type=qtype,
        mode=mode, all_questions=all_questions,
    )
