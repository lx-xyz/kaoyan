"""生成设计说明书配图 -- 学术黑白风格"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

try:
    ft = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 22)
    fh = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 16)
    fn = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 13)
    fs = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 10)
except:
    ft = fh = fn = fs = ImageFont.load_default()

W = (255, 255, 255)
B = (0, 0, 0)
G = (80, 80, 80)
LG = (220, 220, 220)
BG = (255, 255, 255)


def box(d, x, y, w, h, fill=W, outline=B, width=2):
    d.rectangle([x, y, x + w, y + h], fill=fill, outline=outline, width=width)


def rbox(d, x, y, w, h, fill=W, outline=B, width=2):
    d.rounded_rectangle([x, y, x + w, y + h], 4, fill=fill, outline=outline, width=width)


def t(d, x, y, s, font=fn, col=B, anc='la'):
    d.text((x, y), s, font=font, fill=col, anchor=anc)


def ad(d, x, y, col=B):
    d.line([(x, y), (x, y + 15)], fill=col, width=2)
    d.polygon([(x, y + 18), (x - 5, y + 12), (x + 5, y + 12)], fill=col)


def ar(d, x, y, col=B):
    d.line([(x, y), (x + 15, y)], fill=col, width=2)
    d.polygon([(x + 18, y), (x + 12, y - 5), (x + 12, y + 5)], fill=col)


def line(d, x1, y1, x2, y2, col=B, w=1):
    d.line([(x1, y1), (x2, y2)], fill=col, width=w)


def text_center(d, x, y, s, font=fn, col=B):
    t(d, x, y, s, font, col, 'mm')


def draw_border(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=B, width=2)


# ============================================================
# 图1: 系统技术架构图
# ============================================================
img = Image.new('RGB', (780, 520), BG)
d = ImageDraw.Draw(img)
text_center(d, 390, 22, "图1  系统技术架构图", ft, B)

# 前端层
box(d, 30, 50, 720, 100)
text_center(d, 390, 65, "前端展示层", fh, B)
row_items = ["Bootstrap5\n响应式UI", "KaTeX\n公式渲染", "Chart.js\n统计图表", "Quill.js\n富文本编辑", "Jinja2\n模板引擎"]
for i, s in enumerate(row_items):
    x = 55 + i * 140
    box(d, x, 80, 120, 55, LG)
    lines = s.split('\n')
    for j, line_text in enumerate(lines):
        text_center(d, x + 60, 92 + j * 16, line_text, fs, B)

# 箭头
ad(d, 390, 155)

# 应用层
box(d, 30, 180, 720, 200)
text_center(d, 390, 195, "Web 应用层 (Flask 3.1)", fh, B)
app_layers = [
    ("路由层 (routes/)", "11个路由模块: main auth exam mistake vocab note timer import settings admin user"),
    ("业务逻辑层 (services/)", "spaced_repetition.py: 艾宾浩斯记忆曲线间隔复习算法"),
    ("数据访问层 (SQLAlchemy)", "16个ORM模型类, 对象关系映射, 参数化查询"),
    ("表单验证层 (WTForms)", "用户输入验证, 密码加密(bcrypt), 唯一性校验"),
]
for i, (left, right) in enumerate(app_layers):
    y = 218 + i * 36
    rbox(d, 50, y, 200, 30, LG)
    text_center(d, 150, y + 15, left, fs, B)
    rbox(d, 270, y, 460, 30, LG)
    text_center(d, 500, y + 15, right, fs, G)

# 箭头
ad(d, 390, 385)

# 数据层
box(d, 160, 410, 460, 80)
text_center(d, 390, 425, "数据存储层 (SQLite)", fh, B)
text_center(d, 390, 450, "kaoyan.db - 16张数据表 - 单文件存储", fn, B)
text_center(d, 390, 470, "user | subject | exam_question | exam_record | mistake_item | vocabulary_word | note | study_session | ...", fs, G)

img.save(os.path.join(OUT_DIR, "图1_系统技术架构图.png"))
print("图1 OK")


# ============================================================
# 图2: 数据库ER关系图
# ============================================================
img = Image.new('RGB', (780, 480), BG)
d = ImageDraw.Draw(img)
text_center(d, 390, 22, "图2  数据库ER关系图", ft, B)

# SUBJECT
rbox(d, 310, 50, 160, 40, LG); text_center(d, 390, 70, "SUBJECT 科目", fh, B)

# USER
rbox(d, 50, 140, 200, 55, LG)
text_center(d, 150, 157, "USER 用户", fh, B)
text_center(d, 150, 178, "id username password nickname", fs, G)

# EXAM_QUESTION
rbox(d, 310, 140, 200, 55, LG)
text_center(d, 410, 157, "EXAM_QUESTION 题目", fh, B)
text_center(d, 410, 178, "id title options answer analysis", fs, G)

# MISTAKE_ITEM
rbox(d, 570, 140, 180, 55, LG)
text_center(d, 660, 157, "MISTAKE_ITEM 错题本", fh, B)
text_center(d, 660, 178, "id mastery_level next_review", fs, G)

# 连线
line(d, 250, 167, 310, 167, G, 1)  # USER -> EXAM
line(d, 510, 167, 570, 167, G, 1)  # EXAM -> MISTAKE
line(d, 390, 90, 390, 140, G, 1)   # SUBJECT -> EXAM
d.line([(390, 90), (390, 140)], fill=G, width=1)

# 子表
sub_tables = [
    "exam_record 做题记录",
    "vocabulary_word 单词",
    "note 笔记",
    "study_session 学习记录",
    "workbook 习题册",
    "user_image 用户图库",
    "import_log 导入日志",
]
for i, s in enumerate(sub_tables):
    y = 230 + i * 28
    box(d, 30, y, 180, 24)
    text_center(d, 120, y + 12, s, fs, B)
    line(d, 210, y + 12, 250, y + 12, G, 1)

# 关系说明
rbox(d, 320, 300, 420, 70, LG)
text_center(d, 530, 320, "关联关系:", fh, B)
text_center(d, 530, 340, "User 1:N exam_record, mistake_item, vocabulary_word, note, study_session, workbook", fn, G)
text_center(d, 530, 358, "Subject 1:N exam_question, workbook  |  Workbook N:M exam_question (via workbook_question)", fn, G)

# 图例
rbox(d, 320, 395, 420, 55, LG)
text_center(d, 530, 410, "图例:  矩形框=实体表   连线=外键关系   1:N=一对多   N:M=多对多", fn, G)

img.save(os.path.join(OUT_DIR, "图2_数据库ER关系图.png"))
print("图2 OK")


# ============================================================
# 图3: 艾宾浩斯记忆曲线算法
# ============================================================
img = Image.new('RGB', (780, 380), BG)
d = ImageDraw.Draw(img)
text_center(d, 390, 22, "图3  艾宾浩斯记忆曲线间隔复习算法", ft, B)

# 阶段框
stages = [("阶段0", "10分钟"), ("阶段1", "1天"), ("阶段2", "3天"), ("阶段3", "7天"), ("阶段4", "15天"), ("阶段5", "已掌握")]
for i, (n, v) in enumerate(stages):
    x = 35 + i * 120
    fill = LG if i < 5 else W
    rbox(d, x, 55, 105, 45, fill)
    text_center(d, x + 52, 68, n, fh, B)
    text_center(d, x + 52, 88, v, fn, G)
    if i < 5:
        ar(d, x + 110, 77, B)

# 反馈箭头
text_center(d, 390, 120, "正确/认识 -> 推进     错误/不认识 -> 重置为阶段0", fn, B)

# 曲线示意
d.line([(50, 320), (100, 210), (160, 180), (270, 170), (450, 260)], fill=B, width=2)
pts = [(50, 320), (100, 210), (160, 180), (270, 170), (450, 260)]
for x, y in pts:
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=B)
labels = [("首次学习", 50, 335), ("10min", 100, 195), ("1天", 160, 195), ("3天", 250, 155), ("7天", 350, 180), ("15天", 460, 270)]
for s, x, y in labels:
    text_center(d, x, y, s, fs, G)

text_center(d, 390, 350, "遗忘曲线: 间隔复习对抗遗忘，每次复习后遗忘速度减慢", fn, G)

img.save(os.path.join(OUT_DIR, "图3_记忆曲线算法.png"))
print("图3 OK")


# ============================================================
# 图4: 系统功能模块结构图
# ============================================================
img = Image.new('RGB', (780, 360), BG)
d = ImageDraw.Draw(img)
text_center(d, 390, 22, "图4  系统功能模块结构图", ft, B)

mods = [
    ("用户系统", "注册/登录/游客"), ("题目管理", "录入/编辑/列表"),
    ("做题练习", "随机/选题/判分"), ("错题追踪", "自动收集/曲线复习"),
    ("单词记忆", "学习卡片/回炉/复习"), ("笔记记录", "富文本编辑"),
    ("专注计时", "番茄钟/学习记录"), ("批量导入", "粘贴解析/Excel"),
]
for i, (n, dsc) in enumerate(mods):
    x = 25 + i * 95
    box(d, x, 55, 85, 60)
    text_center(d, x + 42, 72, n, fs, B)
    lines = dsc.split('/')
    for j, ln in enumerate(lines):
        text_center(d, x + 42, 92 + j * 14, ln, fs, G)

bot = [
    ("仪表盘", "统计/倒计时/语录"), ("管理后台", "Hero图/图库/科目"),
    ("系统设置", "图片上传/科目管理"), ("学习统计", "Chart.js图表"),
]
for i, (n, dsc) in enumerate(bot):
    x = 95 + i * 160
    box(d, x, 140, 140, 45)
    text_center(d, x + 70, 155, n, fn, B)
    text_center(d, x + 70, 172, dsc, fs, G)

rbox(d, 80, 210, 620, 45, LG)
text_center(d, 390, 225, "全部功能模块通过导航栏 + 仪表盘快捷入口串联", fn, B)
text_center(d, 390, 242, "用户登录后进入仪表盘 -> 选择功能 -> 开始学习", fn, G)

# 用户角色
rbox(d, 80, 275, 280, 40, LG); text_center(d, 220, 295, "管理员: 全部权限 + 管理后台", fn, B)
rbox(d, 420, 275, 280, 40, LG); text_center(d, 560, 295, "普通用户: 学习功能 + 个人设置", fn, B)

img.save(os.path.join(OUT_DIR, "图4_功能模块结构图.png"))
print("图4 OK")


# ============================================================
# 图5: 页面导航结构图
# ============================================================
img = Image.new('RGB', (780, 420), BG)
d = ImageDraw.Draw(img)
text_center(d, 390, 22, "图5  系统页面导航结构图", ft, B)

rbox(d, 280, 45, 220, 40); text_center(d, 390, 65, "首页 (index.html)", fn, B)
ad(d, 300, 90); ad(d, 390, 90); ad(d, 480, 90)
for n, x in [("注册", 260), ("登录", 390), ("游客体验", 515)]:
    box(d, x - 45, 115, 80, 30); text_center(d, x - 5, 130, n, fs, B)

for x in [280, 390, 490]: ad(d, x, 148)
rbox(d, 230, 172, 320, 45); text_center(d, 390, 194, "仪表盘 (dashboard.html)", fh, B)
ad(d, 390, 220)

pages = ["做题\npractice", "题库\nexam", "错题本\nmistake", "单词本\nvocab", "笔记\nnote", "计时器\ntimer", "统计\nstats", "导入\nimport"]
for i, s in enumerate(pages):
    x = 30 + i * 95
    box(d, x, 245, 80, 50)
    lines = s.split('\n')
    for j, ln in enumerate(lines):
        text_center(d, x + 40, 258 + j * 18, ln, fs, B)

rbox(d, 100, 320, 580, 45, LG)
pages2 = ["个人中心 profile", "编辑资料 profile_edit", "管理后台 admin", "系统设置 settings", "学习词汇 learn", "复习词汇 review"]
text_center(d, 390, 340, " / ".join(pages2), fs, G)

text_center(d, 390, 385, "共 20+ 个页面 | 11 个路由模块 | 47 个模板文件 | Bootstrap 5.3 响应式布局", fn, B)

img.save(os.path.join(OUT_DIR, "图5_页面导航结构图.png"))
print("图5 OK")


# ============================================================
# 图6: 用户注册登录流程图
# ============================================================
img = Image.new('RGB', (550, 420), BG)
d = ImageDraw.Draw(img)
text_center(d, 275, 22, "图6  用户注册/登录/游客流程图", ft, B)

rbox(d, 175, 45, 200, 35); text_center(d, 275, 62, "访问首页", fn, B)
ad(d, 275, 85)

for n, x in [("注册", 120), ("登录", 275), ("游客体验", 430)]:
    rbox(d, x - 45, 110, 85, 32); text_center(d, x - 2, 126, n, fs, B)
ad(d, 120, 145); ad(d, 275, 145); ad(d, 430, 145)

rbox(d, 70, 170, 115, 50); text_center(d, 127, 185, "填写表单\n用户名+密码", fs, B); text_center(d, 127, 208, "(无邮箱)", fs, G)
rbox(d, 240, 170, 70, 50); text_center(d, 275, 185, "验证\n密码", fs, B)
rbox(d, 390, 170, 115, 50); text_center(d, 447, 185, "自动生成\n临时账号", fs, B)
ad(d, 127, 225); ad(d, 275, 225); ad(d, 447, 225)

rbox(d, 70, 250, 115, 35, LG); text_center(d, 127, 267, "bcrypt加密", fs, B)
rbox(d, 240, 250, 70, 35, LG); text_center(d, 275, 267, "正确?", fs, B)
rbox(d, 390, 250, 115, 35, LG); text_center(d, 447, 267, "is_guest=True", fs, B)

line(d, 127, 290, 127, 320, B, 1)
line(d, 275, 290, 275, 320, B, 1)
line(d, 447, 290, 447, 320, B, 1)

rbox(d, 80, 320, 100, 40, LG); text_center(d, 130, 340, "创建成功\n自动登录", fs, B)
rbox(d, 220, 320, 110, 40, LG)
text_center(d, 275, 330, "正确:", fs, B); text_center(d, 275, 350, "登录->仪表盘", fs, G)
rbox(d, 380, 320, 130, 40, LG); text_center(d, 445, 340, "可使用系统\n退出清数据", fs, B)

line(d, 275, 360, 275, 375, B, 1)
rbox(d, 220, 375, 110, 30, LG); text_center(d, 275, 390, "错误: 重新输入", fn, B)

img.save(os.path.join(OUT_DIR, "图6_用户注册登录流程图.png"))
print("图6 OK")


# ============================================================
# 图7: 做题判分流程图
# ============================================================
img = Image.new('RGB', (550, 350), BG)
d = ImageDraw.Draw(img)
text_center(d, 275, 22, "图7  做题练习与判分流程图", ft, B)

rbox(d, 80, 50, 120, 35); text_center(d, 140, 67, "选择科目", fn, B)
rbox(d, 240, 50, 120, 35); text_center(d, 300, 67, "随机出题", fn, B)
rbox(d, 400, 50, 100, 35); text_center(d, 450, 67, "选题练习", fn, B)
ar(d, 200, 67, B); ar(d, 360, 67, B)

ad(d, 140, 90); ad(d, 300, 90); ad(d, 450, 90)

rbox(d, 175, 115, 200, 40); text_center(d, 275, 135, "显示题目 + 选项/输入框", fn, B)
ad(d, 275, 160)
rbox(d, 175, 185, 200, 40); text_center(d, 275, 205, "用户选择答案 / 输入答案", fn, B)
ad(d, 275, 230)

rbox(d, 130, 255, 120, 40, LG); text_center(d, 190, 275, "正确", fn, B)
rbox(d, 310, 255, 120, 40, LG); text_center(d, 370, 275, "错误", fn, B)
ad(d, 190, 300); ad(d, 370, 300)

rbox(d, 80, 320, 170, 30, LG); text_center(d, 165, 335, "绿色边框 + 正确答案标签", fs, B)
rbox(d, 300, 320, 200, 30, LG); text_center(d, 400, 335, "红色边框 + 正确变绿 + 自动入错题本", fs, B)

img.save(os.path.join(OUT_DIR, "图7_做题判分流程图.png"))
print("图7 OK")


# ============================================================
# 图8: 单词学习回炉流程图
# ============================================================
img = Image.new('RGB', (650, 420), BG)
d = ImageDraw.Draw(img)
text_center(d, 325, 22, "图8  单词学习回炉循环流程图", ft, B)

rbox(d, 200, 45, 250, 35); text_center(d, 325, 62, "新词池 (stage = -1)", fn, B)
ad(d, 325, 85)

rbox(d, 130, 108, 390, 50)
text_center(d, 325, 125, "学习卡片: 显示单词 + 释义", fh, B)
text_center(d, 325, 145, "[认识] / [不认识]", fn, B)

ad(d, 240, 162); text_center(d, 220, 175, "认识", fs, B)
ad(d, 410, 162); text_center(d, 435, 175, "不认识", fs, B)

rbox(d, 60, 195, 180, 55); text_center(d, 150, 215, "进入复习周期", fh, B); text_center(d, 150, 235, "stage=0, 1天后复习", fs, G)
rbox(d, 410, 195, 180, 55); text_center(d, 500, 215, "加入回炉队列", fh, B); text_center(d, 500, 235, "保持 stage=-1", fs, G)

ad(d, 500, 255)
rbox(d, 250, 278, 350, 55, LG)
text_center(d, 425, 295, "本轮全部过完后, 回炉词重新出现", fn, B)
text_center(d, 425, 318, "循环直到所有词都点 [认识]", fn, B)

ad(d, 325, 338)
rbox(d, 180, 362, 290, 35, LG)
text_center(d, 325, 379, "全部认识 -> 学习完成!", fn, B)

img.save(os.path.join(OUT_DIR, "图8_单词学习流程图.png"))
print("图8 OK")


# ============================================================
# 图9: 错题追踪流程图
# ============================================================
img = Image.new('RGB', (550, 380), BG)
d = ImageDraw.Draw(img)
text_center(d, 275, 22, "图9  错题追踪流程图", ft, B)

rbox(d, 175, 45, 200, 35); text_center(d, 275, 62, "做错一道题", fn, B)
ad(d, 275, 85)

rbox(d, 130, 108, 290, 45); text_center(d, 275, 122, "检查错题本是否已有该题", fh, B); text_center(d, 275, 142, "已有: wrong_count+1, mastery-1 | 无: 新建记录", fs, G)
ad(d, 275, 158)

rbox(d, 130, 180, 290, 50, LG)
text_center(d, 275, 195, "设定下次复习时间 = 10分钟后", fn, B)
text_center(d, 275, 218, "状态: active (待复习)", fs, G)
ad(d, 275, 235)

rbox(d, 150, 258, 250, 55)
text_center(d, 275, 278, "到期后进入错题复习页", fn, B)
text_center(d, 275, 298, "重新作答 -> 判分", fn, G)
ad(d, 275, 318)

rbox(d, 100, 338, 160, 35, LG); text_center(d, 180, 355, "正确 -> 推进阶段", fs, B)
rbox(d, 290, 338, 160, 35, LG); text_center(d, 370, 355, "错误 -> 重置阶段", fs, B)

img.save(os.path.join(OUT_DIR, "图9_错题追踪流程图.png"))
print("图9 OK")


# ============================================================
# 图10: 部署架构图
# ============================================================
img = Image.new('RGB', (650, 280), BG)
d = ImageDraw.Draw(img)
text_center(d, 325, 22, "图10  系统部署架构图", ft, B)

rbox(d, 200, 45, 250, 35); text_center(d, 325, 62, "用户浏览器 (电脑/平板/手机)", fn, B)
ad(d, 220, 85); ad(d, 430, 85)


rbox(d, 80, 120, 200, 60); text_center(d, 180, 140, "PythonAnywhere", fh, B)
text_center(d, 180, 162, "免费云平台, 7x24在线", fs, G)

rbox(d, 370, 120, 200, 60); text_center(d, 470, 140, "本地 EXE 文件", fh, B)
text_center(d, 470, 162, "双击运行, 无需安装Python", fs, G)

ad(d, 180, 185); ad(d, 470, 185)

rbox(d, 175, 208, 300, 45); text_center(d, 325, 222, "Flask Web 应用 (端口5000)", fh, B)
text_center(d, 325, 242, "Jinja2模板引擎 + Bootstrap5前端", fn, G)

ad(d, 325, 258)
rbox(d, 200, 265, 250, 30, LG); text_center(d, 325, 280, "SQLite 数据库 (kaoyan.db)", fn, B)

img.save(os.path.join(OUT_DIR, "图10_系统部署架构图.png"))
print("图10 OK")

print(f"\n全部10张图生成完毕: {os.path.abspath(OUT_DIR)}")
