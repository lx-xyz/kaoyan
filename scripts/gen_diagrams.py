import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

try:
    ft = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 24)
    fh = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 18)
    fn = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 13)
    fs = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 10)
except:
    ft = fh = fn = fs = ImageFont.load_default()

W = (255, 255, 255)
B = (30, 30, 30)
G = (120, 120, 120)
GOLD = (232, 168, 23)
CORAL = (232, 115, 74)
GREEN = (91, 154, 90)
RED = (209, 82, 74)
BLUE = (74, 143, 200)
BG = (250, 248, 245)
BORDER = (220, 215, 205)


def box(d, x, y, w, h, fill=W, outline=BORDER):
    d.rounded_rectangle([x, y, x + w, y + h], 8, fill=fill, outline=outline)


def t(d, x, y, s, font=fn, col=B, anc='la'):
    d.text((x, y), s, font=font, fill=col, anchor=anc)


def ad(d, x, y, col=G):
    d.line([(x, y), (x, y + 15)], fill=col, width=2)
    d.polygon([(x, y + 18), (x - 5, y + 12), (x + 5, y + 12)], fill=col)


def ar(d, x, y, col=G):
    d.line([(x, y), (x + 15, y)], fill=col, width=2)
    d.polygon([(x + 18, y), (x + 12, y - 5), (x + 12, y + 5)], fill=col)


# ====== 1 ======
img = Image.new('RGB', (880, 600), BG)
d = ImageDraw.Draw(img)
t(d, 440, 25, "系统技术架构图", ft, B, 'mt')
box(d, 40, 55, 800, 110, (240, 248, 255), BORDER)
t(d, 440, 70, "前端展示层 (Browser)", fh, BLUE, 'mt')
for i, s in enumerate(["Bootstrap 5.3", "KaTeX 公式", "Chart.js 图表", "Quill.js 编辑器"]):
    x = 70 + i * 200
    box(d, x, 95, 170, 50, W, BORDER)
    t(d, x + 85, 120, s, fn, B, 'mm')
ad(d, 440, 170, BLUE)
box(d, 40, 195, 800, 210, (255, 248, 235), BORDER)
t(d, 440, 210, "Web 应用层 (Flask 3.1)", fh, GOLD, 'mt')
layers = [("路由层", "11个路由模块按功能拆分"), ("业务逻辑层", "spaced_repetition.py 记忆曲线算法"), ("数据访问层", "SQLAlchemy ORM 16个Model类")]
for i, (a, b) in enumerate(layers):
    y = 240 + i * 50
    box(d, 70, y, 180, 40, W, BORDER)
    t(d, 160, y + 20, a, fh, B, 'mm')
    box(d, 270, y, 500, 40, W, BORDER)
    t(d, 520, y + 20, b, fn, G, 'mm')
ad(d, 440, 410, GOLD)
box(d, 40, 435, 800, 130, (240, 255, 240), BORDER)
t(d, 440, 450, "数据存储层 (SQLite)", fh, GREEN, 'mt')
box(d, 200, 475, 480, 70, W, BORDER)
t(d, 440, 500, "kaoyan.db - 16张数据表", fh, B, 'mm')
t(d, 440, 525, "user | subject | exam_question | mistake_item | vocabulary_word | ...", fs, G, 'mt')
img.save(os.path.join(OUT_DIR, "01_系统架构图.png"))
print("01 OK")

# ====== 2 ======
img = Image.new('RGB', (880, 480), BG)
d = ImageDraw.Draw(img)
t(d, 440, 20, "数据库 ER 关系图", ft, B, 'mt')
box(d, 340, 45, 200, 40, (255, 245, 230), GOLD)
t(d, 440, 65, "SUBJECT 科目", fh, B, 'mm')
box(d, 340, 140, 200, 60, W, BORDER)
t(d, 440, 160, "EXAM_QUESTION", fh, B, 'mm')
t(d, 440, 180, "题目数据表", fs, G, 'mt')
ar(d, 540, 170, G)
box(d, 570, 130, 250, 80, W, BORDER)
t(d, 695, 155, "MISTAKE_ITEM", fh, B, 'mm')
t(d, 695, 178, "错题追踪表", fs, G, 'mt')
ad(d, 440, 90, G)
box(d, 60, 140, 220, 60, (255, 248, 235), GOLD)
t(d, 170, 160, "USER 用户表", fh, B, 'mm')
t(d, 170, 180, "核心实体", fs, G, 'mt')
ar(d, 280, 170, G)
tables = ["exam_record 做题记录", "vocabulary_word 单词", "note 笔记", "study_session 学习记录", "user_image 用户图库", "workbook 习题册"]
for i, s in enumerate(tables):
    y = 240 + i * 32
    box(d, 40, y, 180, 26, W, BORDER)
    t(d, 50, y + 13, s, fs, B, 'lm')
    d.line([(225, y + 13), (250, y + 13)], fill=G, width=1)
box(d, 400, 340, 400, 80, W, BORDER)
t(d, 600, 365, "关联关系说明:", fh, B, 'mm')
t(d, 600, 390, "User 1:N 记录/错题/单词/笔记/计时 | Subject 1:N 题目/习题册", fs, G, 'mt')
img.save(os.path.join(OUT_DIR, "02_ER关系图.png"))
print("02 OK")

# ====== 3 ======
img = Image.new('RGB', (800, 350), BG)
d = ImageDraw.Draw(img)
t(d, 400, 20, "艾宾浩斯记忆曲线算法", ft, B, 'mt')
stages = [("阶段0", "10min", GOLD), ("阶段1", "1天", CORAL), ("阶段2", "3天", CORAL), ("阶段3", "7天", CORAL), ("阶段4", "15天", CORAL), ("阶段5", "掌握", GREEN)]
for i, (n, v, c) in enumerate(stages):
    x = 50 + i * 125
    bcol = (240, 255, 240) if i == 5 else (255, 250, 240)
    box(d, x, 60, 105, 50, bcol, c)
    t(d, x + 52, 75, n, fh, c, 'mt')
    t(d, x + 52, 95, v, fs, G, 'mt')
    if i < 5:
        ar(d, x + 110, 85, c)
t(d, 400, 140, "认识/正确 -> 推进    不认识/错误 -> 重置为阶段0", fn, G, 'mt')
pts = [(50, 280), (100, 180), (160, 145), (270, 135), (400, 240)]
for x, y in pts:
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=GOLD)
labels = [("学习", 50, 295), ("10min", 100, 165), ("1天", 170, 145), ("3天", 280, 140), ("7天", 360, 160), ("15天", 410, 250)]
for s, x, y in labels:
    t(d, x, y, s, fs, G, 'mt')
img.save(os.path.join(OUT_DIR, "03_记忆曲线算法.png"))
print("03 OK")

# ====== 4 ======
img = Image.new('RGB', (800, 450), BG)
d = ImageDraw.Draw(img)
t(d, 400, 20, "系统页面导航结构图", ft, B, 'mt')
box(d, 280, 45, 240, 40, (255, 248, 235), GOLD)
t(d, 400, 65, "首页 (全屏大图)", fh, B, 'mm')
for x in [300, 400, 500]:
    ad(d, x, 88, G)
for n, x in [("注册", 255), ("登录", 395), ("游客", 535)]:
    box(d, x - 55, 110, 100, 32, W, BORDER)
    t(d, x - 5, 126, n, fn, B, 'mm')
for x in [275, 400, 525]:
    ad(d, x, 145, G)
box(d, 250, 168, 300, 45, (255, 248, 235), GOLD)
t(d, 400, 190, "仪表盘 (登录后首页)", fh, B, 'mm')
ad(d, 400, 215, G)
feats = ["做题", "题库", "错题", "单词", "笔记", "计时", "统计", "导入"]
for i, s in enumerate(feats):
    x = 40 + i * 95
    box(d, x, 240, 80, 35, W, BORDER)
    t(d, x + 40, 257, s, fn, B, 'mm')
t(d, 400, 310, "所有页面通过导航栏 + 仪表盘入口串联", fn, G, 'mt')
box(d, 200, 340, 400, 50, (240, 255, 240), GREEN)
t(d, 400, 365, "响应式适配: 电脑 | 平板 | 手机 均正常显示", fn, GREEN, 'mm')
img.save(os.path.join(OUT_DIR, "04_页面导航图.png"))
print("04 OK")

# ====== 5 ======
img = Image.new('RGB', (840, 300), BG)
d = ImageDraw.Draw(img)
t(d, 420, 20, "系统功能模块结构图", ft, B, 'mt')
mods = [("用户系统", "注册/登录/游客", GOLD), ("题目管理", "录入/编辑/列表", CORAL), ("做题练习", "随机/选题/判分", GREEN), ("错题追踪", "自动收集/曲线复习", RED), ("单词记忆", "卡片学习/回炉/复习", BLUE), ("笔记记录", "富文本/分类/置顶", (108, 92, 231)), ("专注计时", "番茄钟/统计", GREEN), ("批量导入", "粘贴解析/Excel", CORAL)]
for i, (n, dsc, c) in enumerate(mods):
    x = 25 + i * 100
    box(d, x, 60, 90, 70, W, c)
    t(d, x + 45, 80, n, fs, c, 'mt')
    t(d, x + 45, 110, dsc, fs, G, 'mt')
bot = [("仪表盘", "统计/倒计时/语录", 110), ("管理后台", "Hero图/图库/科目", 300), ("系统设置", "图片上传/科目管理", 490), ("学习统计", "Chart.js图表", 680)]
for n, dsc, x in bot:
    box(d, x, 160, 120, 40, W, BORDER)
    t(d, x + 60, 175, n, fn, B, 'mt')
    t(d, x + 60, 190, dsc, fs, G, 'mt')
box(d, 80, 230, 680, 35, (240, 248, 255), BLUE)
t(d, 420, 247, "全部模块通过导航栏串联，形成完整学习工作流", fn, BLUE, 'mm')
img.save(os.path.join(OUT_DIR, "05_功能模块结构图.png"))
print("05 OK")

# ====== 6 ======
img = Image.new('RGB', (700, 420), BG)
d = ImageDraw.Draw(img)
t(d, 350, 20, "单词学习 - 回炉循环流程", ft, B, 'mt')
box(d, 210, 45, 280, 40, (240, 248, 255), BLUE)
t(d, 350, 65, "新词池 (stage=-1)", fh, B, 'mm')
ad(d, 350, 88, BLUE)
box(d, 150, 110, 400, 55, W, GOLD)
t(d, 350, 130, "学习卡片 - 显示单词 + 释义", fh, B, 'mt')
t(d, 350, 150, "[认识] / [不认识]", fn, G, 'mt')
ad(d, 260, 168, GREEN)
ad(d, 440, 168, RED)
t(d, 240, 180, "认识", fs, GREEN, 'mt')
t(d, 460, 180, "不认识", fs, RED, 'mt')
box(d, 120, 195, 170, 45, (240, 255, 240), GREEN)
t(d, 205, 210, "进入复习周期", fh, GREEN, 'mm')
t(d, 205, 230, "stage=0, 1天后复习", fs, G, 'mt')
box(d, 420, 195, 170, 45, (255, 240, 240), RED)
t(d, 505, 210, "加入回炉队列", fh, RED, 'mm')
t(d, 505, 230, "保持 stage=-1", fs, G, 'mt')
ad(d, 505, 242, RED)
box(d, 200, 265, 450, 60, (255, 248, 230), GOLD)
t(d, 425, 285, "本轮全部过完 -> 回炉词重新出现", fh, B, 'mt')
t(d, 425, 308, "循环直到所有词都点 [认识]", fn, G, 'mt')
ad(d, 350, 328, GREEN)
box(d, 200, 350, 300, 40, (240, 255, 240), GREEN)
t(d, 350, 370, "全部认识！学习完成", fh, GREEN, 'mm')
img.save(os.path.join(OUT_DIR, "06_单词学习流程图.png"))
print("06 OK")
print("Done:", os.path.abspath(OUT_DIR))
