import os
import io
import re
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, jsonify
from flask_login import login_required, current_user
import pandas as pd
from app import db
from app.models import get_visible_subjects, Subject, ExamQuestion, VocabularyWord, ImportLog

import_bp = Blueprint("import_data", __name__)

EXAM_COLUMNS = ["科目代码", "年份", "来源", "题型", "题号", "题干", "选项A", "选项B", "选项C", "选项D", "正确答案", "解析", "难度", "标签"]
VOCAB_COLUMNS = ["单词", "音标", "释义", "例句", "例句翻译", "词性"]


@import_bp.route("/import", methods=["GET", "POST"])
@login_required
def import_page():
    logs = ImportLog.query.filter_by(user_id=current_user.id).order_by(ImportLog.created_at.desc()).limit(10).all()
    subjects = get_visible_subjects(current_user.id).all()
    parsed = []
    subject_id = None
    year = None
    source = ""

    # 粘贴解析
    if request.method == "POST" and "parse" in request.form:
        subject_id = request.form.get("subject_id", type=int)
        year = request.form.get("year", type=int) or None
        source = request.form.get("source", "")
        text = request.form.get("raw_text", "")
        parsed = _parse_questions(text)
        if not parsed:
            flash("未能识别出题目，请检查格式后重试。", "warning")

    # 批量保存解析结果
    if request.method == "POST" and "save_parsed" in request.form:
        subject_id = request.form.get("subject_id", type=int)
        year = request.form.get("year", type=int) or None
        source = request.form.get("source", "")
        count = int(request.form.get("parsed_count", 0))
        saved = 0
        for i in range(count):
            title = request.form.get(f"title_{i}", "").strip()
            q = ExamQuestion(
                subject_id=subject_id, year=year, source=source,
                question_type=request.form.get(f"qtype_{i}", "单选"),
                title=title,
                option_a=request.form.get(f"opt_a_{i}", ""),
                option_b=request.form.get(f"opt_b_{i}", ""),
                option_c=request.form.get(f"opt_c_{i}", ""),
                option_d=request.form.get(f"opt_d_{i}", ""),
                correct_answer=request.form.get(f"answer_{i}", ""),
                analysis=request.form.get(f"analysis_{i}", ""),
                passage_text=request.form.get(f"passage_{i}", ""),
                difficulty=3, created_by=current_user.id,
            )
            db.session.add(q)
            saved += 1
        db.session.commit()
        flash(f"成功保存 {saved} 道题！", "success")
        return redirect(url_for("import_data.import_page"))

    return render_template("import/index.html", logs=logs, subjects=subjects,
                           parsed=parsed, subject_id=subject_id, year=year, source=source)


@import_bp.route("/import/template/exam")
@login_required
def download_exam_template():
    """下载真题导入模板"""
    df = pd.DataFrame(columns=EXAM_COLUMNS)
    # 示例行
    df.loc[0] = ["math", 2024, "2024年真题", "单选", 1, "设 $f(x)=x^2$，求 $f'(1)$", "0", "1", "2", "3", "C", "$f'(x)=2x$，代入得2", 2, "导数"]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="真题导入")
    output.seek(0)
    return send_file(output, download_name="真题导入模板.xlsx", as_attachment=True)


@import_bp.route("/import/template/vocab")
@login_required
def download_vocab_template():
    """下载单词导入模板"""
    df = pd.DataFrame(columns=VOCAB_COLUMNS)
    df.loc[0] = ["abandon", "/ə'bændən/", "放弃", "They had to abandon the plan.", "他们不得不放弃计划。", "v"]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="单词导入")
    output.seek(0)
    return send_file(output, download_name="单词导入模板.xlsx", as_attachment=True)


@import_bp.route("/import/upload", methods=["POST"])
@login_required
def upload_import():
    import_type = request.form.get("type", "exam")
    file = request.files.get("file")
    if not file or not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        flash("请上传 Excel (.xlsx) 或 CSV 文件。", "warning")
        return redirect(url_for("import_data.import_page"))

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file, engine="openpyxl")
    except Exception as e:
        flash(f"文件读取失败：{e}", "danger")
        return redirect(url_for("import_data.import_page"))

    total = len(df)
    success = 0
    errors = []

    if import_type == "exam":
        success, errors = _import_exam(df)
    elif import_type == "vocab":
        success, errors = _import_vocab(df)

    # 记录导入日志
    log = ImportLog(
        user_id=current_user.id,
        import_type=import_type,
        file_name=file.filename,
        total_rows=total,
        success_rows=success,
        error_rows=len(errors),
        error_detail=str(errors[:20]) if errors else None,
    )
    db.session.add(log)
    db.session.commit()

    if errors:
        flash(f"导入完成：成功 {success} 条，失败 {len(errors)} 条。", "warning")
    else:
        flash(f"全部导入成功！共 {success} 条。", "success")

    return redirect(url_for("import_data.import_page"))


def _import_exam(df):
    success = 0
    errors = []
    subject_map = {s.code: s.id for s in Subject.query.all()}

    for idx, row in df.iterrows():
        try:
            code = str(row.get("科目代码", "")).strip()
            subject_id = subject_map.get(code)
            if not subject_id:
                errors.append(f"行{idx+2}: 无效科目代码 '{code}'")
                continue

            qtype = str(row.get("题型", "单选")).strip()
            if qtype not in ["单选", "多选", "填空", "解答", "阅读", "完形", "翻译", "写作", "编程"]:
                qtype = "单选"

            year = row.get("年份")
            if pd.isna(year):
                year = None
            else:
                try:
                    year = int(year)
                except (ValueError, TypeError):
                    year = None

            difficulty = row.get("难度", 3)
            if pd.isna(difficulty):
                difficulty = 3
            else:
                try:
                    difficulty = int(difficulty)
                    if difficulty < 1:
                        difficulty = 1
                    if difficulty > 5:
                        difficulty = 5
                except (ValueError, TypeError):
                    difficulty = 3

            qnum = row.get("题号")
            if pd.isna(qnum):
                qnum = None
            else:
                try:
                    qnum = int(qnum)
                except (ValueError, TypeError):
                    qnum = None

            def safe_str(val):
                return str(val) if not pd.isna(val) else ""

            q = ExamQuestion(
                subject_id=subject_id,
                year=year,
                source=safe_str(row.get("来源")),
                question_type=qtype,
                question_number=qnum,
                title=safe_str(row.get("题干")),
                option_a=safe_str(row.get("选项A")),
                option_b=safe_str(row.get("选项B")),
                option_c=safe_str(row.get("选项C")),
                option_d=safe_str(row.get("选项D")),
                correct_answer=safe_str(row.get("正确答案")),
                analysis=safe_str(row.get("解析")),
                difficulty=difficulty,
                tags=safe_str(row.get("标签")),
                created_by=current_user.id,
            )
            db.session.add(q)
            success += 1
        except Exception as e:
            errors.append(f"行{idx+2}: {str(e)}")

    db.session.commit()
    return success, errors


def _import_vocab(df):
    success = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            def safe_str(val):
                return str(val).strip() if not pd.isna(val) else ""

            word_text = safe_str(row.get("单词"))
            meaning = safe_str(row.get("释义"))
            if not word_text or not meaning:
                errors.append(f"行{idx+2}: 单词或释义为空")
                continue

            existing = VocabularyWord.query.filter_by(
                user_id=current_user.id, word=word_text
            ).first()
            if existing:
                errors.append(f"行{idx+2}: 单词 '{word_text}' 已存在")
                continue

            w = VocabularyWord(
                user_id=current_user.id,
                word=word_text,
                phonetic=safe_str(row.get("音标")),
                meaning=meaning,
                example_sentence=safe_str(row.get("例句")),
                example_translation=safe_str(row.get("例句翻译")),
                part_of_speech=safe_str(row.get("词性")),
                review_stage=-1,
            )
            db.session.add(w)
            success += 1
        except Exception as e:
            errors.append(f"行{idx+2}: {str(e)}")

    db.session.commit()
    return success, errors


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
        if not has_options and not has_answer and not has_question_num and len(first) > 20:
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
