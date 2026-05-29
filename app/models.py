from datetime import datetime, timedelta
from flask_login import UserMixin
from app import db, login_manager


def get_visible_subjects(user_id):
    """获取用户可见的科目：默认 + 自己创建的，去掉隐藏的"""
    from sqlalchemy import or_
    hidden_ids = [h.subject_id for h in HiddenSubject.query.filter_by(user_id=user_id).all()]
    q = Subject.query.filter(
        or_(Subject.is_default == True, Subject.user_id == user_id)
    )
    if hidden_ids:
        q = q.filter(~Subject.id.in_(hidden_ids))
    return q.order_by(Subject.sort_order)


# ============================================================
# 1. user — 用户表
# ============================================================
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(64), default="")
    target_school = db.Column(db.String(128), default="")
    target_major = db.Column(db.String(128), default="")
    daily_goal_hours = db.Column(db.Integer, default=4)
    custom_quote = db.Column(db.Text, default="")
    exam_date = db.Column(db.Date, nullable=True)
    is_guest = db.Column(db.Boolean, default=False)
    dashboard_img = db.Column(db.Text, default="")
    timer_img = db.Column(db.Text, default="")
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # 关系
    exam_records = db.relationship("ExamRecord", backref="user", lazy="dynamic")
    mistake_items = db.relationship("MistakeItem", backref="user", lazy="dynamic")
    vocabulary_words = db.relationship("VocabularyWord", backref="user", lazy="dynamic")
    notes = db.relationship("Note", backref="user", lazy="dynamic")
    study_sessions = db.relationship("StudySession", backref="user", lazy="dynamic")
    workbooks = db.relationship("Workbook", backref="owner", lazy="dynamic")

    def set_password(self, password):
        from app import bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        from app import bcrypt
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


# ============================================================
# 2. subject — 科目表
# ============================================================
class Subject(db.Model):
    __tablename__ = "subject"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(16), nullable=False)
    color = db.Column(db.String(7), default="#FFA000")
    sort_order = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)  # NULL=管理员默认
    is_default = db.Column(db.Boolean, default=False)

    questions = db.relationship("ExamQuestion", backref="subject", lazy="dynamic")

    def __repr__(self):
        return f"<Subject {self.name}>"


# ============================================================
# 3. exam_question — 题目表
# ============================================================
class ExamQuestion(db.Model):
    __tablename__ = "exam_question"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=True)
    source = db.Column(db.String(128), default="")
    question_type = db.Column(db.String(32), default="单选")
    question_number = db.Column(db.Integer, nullable=True)
    title = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=True)
    option_b = db.Column(db.Text, nullable=True)
    option_c = db.Column(db.Text, nullable=True)
    option_d = db.Column(db.Text, nullable=True)
    correct_answer = db.Column(db.String(256), nullable=False)
    analysis = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.Integer, default=3)
    tags = db.Column(db.String(256), default="")
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    passage_text = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    records = db.relationship("ExamRecord", backref="question", lazy="dynamic")
    mistake_items = db.relationship("MistakeItem", backref="question", lazy="dynamic")

    def __repr__(self):
        return f"<ExamQuestion {self.id}: {self.title[:30]}...>"


# ============================================================
# 4. workbook — 习题册表
# ============================================================
class Workbook(db.Model):
    __tablename__ = "workbook"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, default="")
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    question_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    workbook_questions = db.relationship("WorkbookQuestion", backref="workbook",
                                         lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workbook {self.title}>"


# ============================================================
# 5. workbook_question — 习题册-题目关联
# ============================================================
class WorkbookQuestion(db.Model):
    __tablename__ = "workbook_question"

    id = db.Column(db.Integer, primary_key=True)
    workbook_id = db.Column(db.Integer, db.ForeignKey("workbook.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("exam_question.id"), nullable=False)
    sort_order = db.Column(db.Integer, default=0)


# ============================================================
# 6. exam_record — 做题记录
# ============================================================
class ExamRecord(db.Model):
    __tablename__ = "exam_record"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("exam_question.id"), nullable=False)
    user_answer = db.Column(db.String(256), default="")
    is_correct = db.Column(db.Boolean, default=False)
    duration_seconds = db.Column(db.Integer, nullable=True)
    session_type = db.Column(db.String(16), default="practice")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================
# 7. mistake_item — 错题本
# ============================================================
class MistakeItem(db.Model):
    __tablename__ = "mistake_item"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("exam_question.id"), nullable=False)
    wrong_count = db.Column(db.Integer, default=1)
    last_wrong_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_review_at = db.Column(db.DateTime, nullable=True)
    next_review_at = db.Column(db.DateTime, nullable=True)
    mastery_level = db.Column(db.Integer, default=0)
    note = db.Column(db.Text, default="")
    status = db.Column(db.String(16), default="active")

    def __repr__(self):
        return f"<MistakeItem qid={self.question_id} status={self.status}>"


# ============================================================
# 8. vocabulary_word — 单词表
# ============================================================
class VocabularyWord(db.Model):
    __tablename__ = "vocabulary_word"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    word = db.Column(db.String(128), nullable=False)
    phonetic = db.Column(db.String(128), default="")
    meaning = db.Column(db.Text, nullable=False)
    example_sentence = db.Column(db.Text, default="")
    example_translation = db.Column(db.Text, default="")
    part_of_speech = db.Column(db.String(32), default="")
    difficulty = db.Column(db.Integer, default=3)
    review_stage = db.Column(db.Integer, default=-1)
    last_review_at = db.Column(db.DateTime, nullable=True)
    next_review_at = db.Column(db.DateTime, nullable=True)
    review_count = db.Column(db.Integer, default=0)
    is_mastered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<VocabularyWord {self.word}>"


# ============================================================
# 9. note — 笔记表
# ============================================================
class Note(db.Model):
    __tablename__ = "note"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, default="")
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=True)
    category = db.Column(db.String(64), default="")
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Note {self.title}>"


# ============================================================
# 10. study_session — 学习记录
# ============================================================
class StudySession(db.Model):
    __tablename__ = "study_session"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=0)
    session_type = db.Column(db.String(32), default="free")

    def __repr__(self):
        return f"<StudySession {self.duration_minutes}min>"


# ============================================================
# 11. hidden_subject — 用户隐藏的默认科目
# ============================================================
class HiddenSubject(db.Model):
    __tablename__ = "hidden_subject"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)


# ============================================================
# 12. default_image — 默认图库
# ============================================================
class DefaultImage(db.Model):
    __tablename__ = "default_image"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(32), nullable=False)  # dashboard / timer
    url = db.Column(db.Text, nullable=False)


# ============================================================
# 13. system_setting — 系统设置（首页图片等）
# ============================================================
class SystemSetting(db.Model):
    __tablename__ = "system_setting"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, default="")


# ============================================================
# 12. import_log — 导入日志
# ============================================================
class ImportLog(db.Model):
    __tablename__ = "import_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    import_type = db.Column(db.String(32), nullable=False)
    file_name = db.Column(db.String(256), default="")
    total_rows = db.Column(db.Integer, default=0)
    success_rows = db.Column(db.Integer, default=0)
    error_rows = db.Column(db.Integer, default=0)
    error_detail = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
