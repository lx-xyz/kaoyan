from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField,
                     SelectField, IntegerField, TextAreaField)
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from app.models import User

QUESTION_TYPES = [
    ("单选", "单选"), ("多选", "多选"), ("填空", "填空"),
    ("解答", "解答"), ("阅读", "阅读"), ("完形", "完形"),
    ("翻译", "翻译"), ("写作", "写作"), ("编程", "编程"),
]
DIFFICULTY_LEVELS = [(0, "不设置"), (1, "1 — 很简单"), (2, "2 — 简单"), (3, "3 — 中等"), (4, "4 — 较难"), (5, "5 — 很难")]


class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(message="请输入用户名")])
    password = PasswordField("密码", validators=[DataRequired(message="请输入密码")])
    remember = BooleanField("记住我")
    submit = SubmitField("登录")


class RegisterForm(FlaskForm):
    username = StringField("用户名", validators=[
        DataRequired(message="请输入用户名"),
        Length(min=2, max=64, message="用户名长度2~64个字符")
    ])
    password = PasswordField("密码", validators=[DataRequired(message="请输入密码")])
    confirm_password = PasswordField("确认密码", validators=[DataRequired(message="请再次输入密码")])
    submit = SubmitField("注册")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("该用户名已被注册，请换一个。")


class QuestionForm(FlaskForm):
    subject_id = SelectField("科目", coerce=int, validators=[DataRequired(message="请选择科目")])
    year = IntegerField("年份", validators=[Optional()])
    source = StringField("来源", validators=[Length(max=128)])
    question_type = SelectField("题型", choices=QUESTION_TYPES, validators=[DataRequired()])
    question_number = IntegerField("题号", validators=[Optional()])
    title = TextAreaField("题干", validators=[DataRequired(message="请输入题干")])
    option_a = TextAreaField("选项 A")
    option_b = TextAreaField("选项 B")
    option_c = TextAreaField("选项 C")
    option_d = TextAreaField("选项 D")
    correct_answer = StringField("正确答案", validators=[DataRequired(message="请输入正确答案")])
    analysis = TextAreaField("解析")
    difficulty = SelectField("难度", coerce=int, choices=DIFFICULTY_LEVELS, default=3)
    tags = StringField("标签", validators=[Length(max=256)], description="逗号分隔，如：极限,导数")
    submit = SubmitField("保存题目")
