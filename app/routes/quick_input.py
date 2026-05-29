import re
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import get_visible_subjects, Subject, ExamQuestion

quick_bp = Blueprint("quick_input", __name__)


@quick_bp.route("/quick-input", methods=["GET", "POST"])
@login_required
def index():
    parsed = []
    subject_id = request.form.get("subject_id", type=int) if request.method == "POST" else None
    year = request.form.get("year", type=int) if request.method == "POST" else None
    source = request.form.get("source", "") if request.method == "POST" else ""

    if request.method == "POST" and "parse" in request.form:
        text = request.form.get("raw_text", "")
        parsed = _parse_questions(text)
        if not parsed:
            flash("未能识别出题目，请检查格式后重试。", "warning")

    if request.method == "POST" and "save" in request.form:
        saved = _save_parsed(request)
        flash(f"成功保存 {saved} 道题！", "success")
        return redirect(url_for("quick_input.index"))

    subjects = get_visible_subjects(current_user.id).all()
    return render_template(
        "quick_input.html",
        subjects=subjects,
        parsed=parsed,
        subject_id=subject_id,
        year=year,
        source=source,
    )


def _parse_questions(text):
    """从粘贴文本中智能解析题目，自动识别共享文章"""
    if not text or not text.strip():
        return []

    text = text.strip()
    questions = []

    # 按题号拆分
    blocks = []
    current = []
    for line in text.split('\n'):
        line_stripped = line.strip()
        if re.match(r'^\d+[\.\、\)）]\s*\S', line_stripped):
            if current:
                blocks.append('\n'.join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append('\n'.join(current))

    if len(blocks) <= 1:
        blocks = [text]

    # 检测第一个block是否为共享文章（没有ABCD选项和答案）
    shared_passage = ""
    if len(blocks) >= 2:
        first = blocks[0].strip()
        has_options = bool(re.search(r'[A-D][\.\、\)）]', first))
        has_answer = bool(re.search(r'(?:答案|正确答案)', first))
        has_question_num = bool(re.match(r'^\d+[\.\、\)）]', first))
        if not has_options and not has_answer and not has_question_num and len(first) > 40:
            shared_passage = first
            blocks = blocks[1:]

    for block in blocks:
        block = block.strip()
        if not block or len(block) < 5:
            continue

        block = re.sub(r'^\d+[\.\、\)）]\s*', '', block)

        options = {"A": "", "B": "", "C": "", "D": ""}
        # 先规范化：确保每个选项前有换行
        block_norm = re.sub(r'([A-D])[\.\、\)）]', r'\n\1.', block)
        block_norm = re.sub(r'\n+', '\n', block_norm).strip()
        opt_matches = re.findall(
            r'\n\s*([A-D])[\.\、\)）]\s*(.+?)(?=\n\s*[A-D][\.\、\)）]|\n\s*(?:答案|解析|参考|正确|$)|\Z)',
            '\n' + block_norm, re.DOTALL)
        for label, value in opt_matches:
            if label in options:
                options[label] = value.strip()

        title = block
        if options["A"]:
            first_opt = len(block)
            for fmt in [f"\nA.", f"\nA、", f"\nA)", f"\nA）", f"A.", f"A、", f"A)", f"A）"]:
                pos = block.find(fmt)
                if 0 <= pos < first_opt:
                    first_opt = pos
            if first_opt < len(block):
                title = block[:first_opt].strip()

        answer = ""
        ans_match = re.search(r'(?:答案|正确答案|参考答案)[：:\s]*([A-Da-d])', block, re.IGNORECASE)
        if ans_match:
            answer = ans_match.group(1).strip().upper()
        else:
            ans_match = re.search(r'(?:答案|正确答案)[：:\s]*([^\n]{1,30})', block)
            if ans_match:
                val = ans_match.group(1).strip()
                if val and len(val) < 20:
                    answer = val

        analysis = ""
        ana_match = re.search(r'(?:解析|分析|详解)[：:]\s*(.+?)(?=\n\s*(?:答案|参考|正确|\d+[\.\、])|\Z)', block, re.DOTALL)
        if ana_match:
            analysis = ana_match.group(1).strip()

        if options["A"] and options["B"]:
            qtype = "多选" if "多选" in block else "单选"
        elif "填空" in block:
            qtype = "填空"
        elif "解答" in block or "计算" in block or "证明" in block:
            qtype = "解答"
        else:
            qtype = "单选" if options["A"] else "填空"

        questions.append({
            "title": title, "question_type": qtype,
            "option_a": options["A"], "option_b": options["B"],
            "option_c": options["C"], "option_d": options["D"],
            "correct_answer": answer, "analysis": analysis,
            "passage_text": shared_passage,
        })

    return questions


def _save_parsed(req):
    """保存解析后的题目到数据库"""
    saved = 0
    subject_id = req.form.get("subject_id", type=int)
    year = req.form.get("year", type=int) or None
    source = req.form.get("source", "")
    count = int(req.form.get("parsed_count", 0))

    for i in range(count):
        title = req.form.get(f"title_{i}", "").strip()
        if not title:
            continue

        qtype = req.form.get(f"qtype_{i}", "单选")

        q = ExamQuestion(
            subject_id=subject_id,
            year=year,
            source=source,
            question_type=qtype,
            title=title,
            option_a=req.form.get(f"opt_a_{i}", ""),
            option_b=req.form.get(f"opt_b_{i}", ""),
            option_c=req.form.get(f"opt_c_{i}", ""),
            option_d=req.form.get(f"opt_d_{i}", ""),
            correct_answer=req.form.get(f"answer_{i}", ""),
            analysis=req.form.get(f"analysis_{i}", ""),
            difficulty=3,
            created_by=current_user.id,
        )
        db.session.add(q)
        saved += 1

    db.session.commit()
    return saved
