"""生成设计说明书中的图片"""
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

# 颜色
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (100, 100, 100)
LIGHT = (251, 249, 245)
GOLD = (232, 168, 23)
CORAL = (232, 115, 74)
GREEN = (91, 154, 90)
RED = (209, 82, 74)
BLUE = (74, 143, 200)
PURPLE = (108, 92, 231)
CARD = (255, 255, 255)
BORDER = (235, 229, 217)

try:
    font_title = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 28)
    font_h2 = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 20)
    font_normal = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 11)
    font_bold = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 14)
except:
    font_title = ImageFont.load_default()
    font_h2 = ImageFont.load_default()
    font_normal = font_h2
    font_small = font_h2
    font_bold = font_h2


def new_img(w, h, bg=WHITE):
    return Image.new('RGB', (w, h), bg)


def rect(draw, x, y, w, h, fill=CARD, outline=BORDER, radius=8):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline)


def text(draw, x, y, txt, font=font_normal, fill=BLACK, anchor='la'):
    draw.text((x, y), txt, font=font, fill=fill, anchor=anchor)


def arrow_down(draw, x, y, color=GRAY):
    points = [(x, y), (x, y + 20), (x - 5, y + 14), (x + 5, y + 14)]
    draw.line([(x, y), (x, y + 18)], fill=color, width=2)
    draw.polygon([(x, y + 20), (x - 6, y + 12), (x + 6, y + 12)], fill=color)


def arrow_right(draw, x, y, color=GRAY):
    draw.line([(x, y), (x + 18, y)], fill=color, width=2)
    draw.polygon([(x + 20, y), (x + 12, y - 6), (x + 12, y + 6)], fill=color)


# ============ 1. 系统架构图 ============
def draw_architecture():
    img = new_img(900, 650, LIGHT)
    d = ImageDraw.Draw(img)

    # 标题
    text(d, 450, 30, "系统技术架构图", font_title, BLACK, anchor='mt')

    # 前端层
    rect(d, 50, 70, 800, 120, fill=(240, 248, 255))
    text(d, 450, 90, "前端展示层 (Browser)", font_h2, BLUE, anchor='mt')
    items = ["Bootstrap 5.3 响应式UI", "KaTeX 数学公式渲染", "Chart.js 统计图表", "Quill.js 富文本编辑"]
    for i, item in enumerate(items):
        rx = 80 + i * 200
        rect(d, rx, 120, 170, 50, fill=WHITE, outline=BORDER)
        text(d, rx + 85, 145, item, font_small, BLACK, anchor='mm')

    # 箭头
    arrow_down(d, 450, 195, BLUE)

    # 应用层
    rect(d, 50, 220, 800, 220, fill=(255, 248, 240))
    text(d, 450, 240, "Web 应用层 (Flask 3.1)", font_h2, GOLD, anchor='mt')

    layers = [
        ("路由层 (routes/)", "main auth exam mistake vocab note timer"),
        ("表单层 (forms.py)", "WTForms 数据验证"),
        ("业务逻辑层 (services/)", "spaced_repetition.py 记忆曲线算法"),
        ("数据访问层 (SQLAlchemy ORM)", "16个Model类 对象关系映射"),
    ]
    for i, (title, desc) in enumerate(layers):
        y = 265 + i * 42
        rect(d, 80, y, 360, 35, fill=WHITE, outline=BORDER)
        text(d, 95, y + 17, title, font_bold, BLACK, anchor='lm')
        rect(d, 460, y, 360, 35, fill=WHITE, outline=BORDER)
        text(d, 475, y + 17, desc, font_small, GRAY, anchor='lm')

    # 箭头
    arrow_down(d, 450, 445, GOLD)

    # 数据层
    rect(d, 50, 470, 800, 150, fill=(240, 255, 240))
    text(d, 450, 490, "数据存储层 (SQLite)", font_h2, GREEN, anchor='mt')
    rect(d, 200, 515, 500, 80, fill=WHITE, outline=BORDER)
    text(d, 450, 540, "kaoyan.db", font_h2, BLACK, anchor='mm')
    text(d, 450, 565, "16张表：user, subject, exam_question, mistake_item, ...", font_small, GRAY, anchor='mt')

    img.save(os.path.join(OUT_DIR, "01_系统架构图.png"))
    print("01_系统架构图.png OK")


# ============ 2. ER关系图 ============
def draw_er():
    img = new_img(900, 550, LIGHT)
    d = ImageDraw.Draw(img)

    text(d, 450, 25, "数据库 ER 关系图", font_title, BLACK, anchor='mt')

    # Subject
    rect(d, 350, 55, 200, 50, fill=(255, 240, 220), outline=GOLD)
    text(d, 450, 80, "SUBJECT 科目", font_bold, BLACK, anchor='mm')

    # User
    rect(d, 50, 180, 180, 60, fill=(255, 240, 220), outline=GOLD)
    text(d, 140, 200, "USER 用户", font_bold, BLACK, anchor='mm')
    text(d, 140, 220, "id, username, email, is_admin, is_guest", font_small, GRAY, anchor='mt')

    # ExamQuestion
    rect(d, 380, 180, 200, 60, fill=(240, 248, 255), outline=BLUE)
    text(d, 480, 200, "EXAM_QUESTION 题目", font_bold, BLACK, anchor='mm')
    text(d, 480, 220, "id, title, options, answer, analysis", font_small, GRAY, anchor='mt')

    # 关联箭头 (User -> ExamQuestion)
    draw.line([(230, 210), (380, 210)], fill=GRAY, width=1)
    text(d, 305, 200, "录入", font_small, GRAY, anchor='mt')

    # 关联箭头 (Subject -> ExamQuestion)
    draw.line([(450, 105), (450, 180)], fill=GRAY, width=1)
    text(d, 460, 140, "属于", font_small, GRAY, anchor='lm')

    # User关联的子表
    user_tables = [
        ("exam_record", "做题记录"),
        ("mistake_item", "错题本"),
        ("vocabulary_word", "单词"),
        ("note", "笔记"),
        ("study_session", "学习记录"),
        ("workbook", "习题册"),
        ("user_image", "用户图库"),
    ]
    for i, (name, label) in enumerate(user_tables):
        y = 280 + i * 32
        rect(d, 30, y, 90, 25, fill=WHITE, outline=BORDER)
        text(d, 75, y + 12, name, font_small, BLACK, anchor='mm')
        draw.line([(120, y + 12), (140, y + 12)], fill=GRAY, width=1)
        text(d, 145, y + 12, label, font_small, GRAY, anchor='lm')

    # 右侧关联
    rect(d, 680, 280, 180, 50, fill=(255, 240, 220), outline=CORAL)
    text(d, 770, 295, "MISTAKE_ITEM", font_bold, BLACK, anchor='mm')
    text(d, 770, 315, "question_id → 题目", font_small, GRAY, anchor='mt')
    draw.line([(580, 210), (680, 305)], fill=GRAY, width=1)

    # Workbook关联
    rect(d, 680, 380, 180, 50, fill=WHITE, outline=BORDER)
    text(d, 770, 395, "WORKBOOK 习题册", font_bold, BLACK, anchor='mm')
    text(d, 770, 415, "user_id + subject_id", font_small, GRAY, anchor='mt')
    draw.line([(580, 210), (680, 405)], fill=GRAY, width=1)

    img.save(os.path.join(OUT_DIR, "02_ER关系图.png"))
    print("02_ER关系图.png OK")


# ============ 3. 记忆曲线流程图 ============
def draw_memory_curve():
    img = new_img(800, 400, LIGHT)
    d = ImageDraw.Draw(img)

    text(d, 400, 25, "艾宾浩斯记忆曲线 — 间隔复习算法", font_title, BLACK, anchor='mt')

    stages = [
        ("阶段0", "10分钟后", GOLD),
        ("阶段1", "1天后", CORAL),
        ("阶段2", "3天后", CORAL),
        ("阶段3", "7天后", CORAL),
        ("阶段4", "15天后", CORAL),
        ("阶段5", "✓ 已掌握", GREEN),
    ]

    for i, (name, interval, color) in enumerate(stages):
        x = 50 + i * 130
        y = 100
        rect(d, x, y, 110, 50, fill=(255, 250, 240) if i < 5 else (240, 255, 240), outline=color)
        text(d, x + 55, y + 15, name, font_bold, color, anchor='mt')
        text(d, x + 55, y + 33, interval, font_small, GRAY, anchor='mt')

        if i < 5:
            arrow_right(d, x + 115, y + 25, color)

    # 正确/错误标注
    text(d, 400, 180, "认识/正确 → 推进下一个阶段", font_small, GREEN, anchor='mt')
    text(d, 400, 200, "不认识/错误 → 重置回阶段0", font_small, RED, anchor='mt')

    # 遗忘曲线示意
    y0 = 260
    points = [(50, y0 + 100), (80, y0 + 30), (130, y0 + 10), (200, y0 + 5), (400, y0 + 150)]
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=GOLD, width=3)

    # 标注
    for px, py, label in [(50, y0 + 100, "学习"), (80, y0 + 30, "10min"), (130, y0 + 10, "1天"),
                           (200, y0 + 5, "3天"), (300, y0 + 40, "7天"), (380, y0 + 100, "15天")]:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=GOLD)
        if px < 350:
            text(d, px + 10, py - 15, label, font_small, GRAY, anchor='lt')
        else:
            text(d, px - 10, py - 15, label, font_small, GRAY, anchor='rt')

    text(d, 400, y0 + 135, "← 遗忘曲线：间隔复习对抗遗忘 →", font_small, GRAY, anchor='mt')

    img.save(os.path.join(OUT_DIR, "03_记忆曲线算法.png"))
    print("03_记忆曲线算法.png OK")


# ============ 4. 页面导航图 ============
def draw_navigation():
    img = new_img(850, 500, LIGHT)
    d = ImageDraw.Draw(img)

    text(d, 425, 25, "系统页面导航结构图", font_title, BLACK, anchor='mt')

    # 首页
    rect(d, 325, 55, 200, 45, fill=(255, 248, 230), outline=GOLD)
    text(d, 425, 77, "首页 (全屏大图)", font_bold, BLACK, anchor='mm')

    # 箭头
    for x in [310, 420, 530]:
        arrow_down(d, x, 105, GRAY)

    # 注册/登录/游客
    auth_items = [("注册", 180), ("登录", 425), ("游客体验", 670)]
    for name, cx in auth_items:
        rect(d, cx - 75, 130, 120, 35, fill=WHITE, outline=BORDER)
        text(d, cx, 147, name, font_normal, BLACK, anchor='mm')

    # 汇聚
    for cx in [200, 425, 665]:
        arrow_down(d, cx, 168, GRAY)

    # 仪表盘
    rect(d, 300, 195, 250, 50, fill=(255, 248, 230), outline=GOLD)
    text(d, 425, 220, "📊 仪表盘 (登录后首页)", font_bold, BLACK, anchor='mm')

    arrow_down(d, 425, 250, GRAY)

    # 功能入口
    features = [
        ("开始做题", "exam/practice", 50),
        ("题库管理", "exam", 180),
        ("错题追踪", "mistake", 310),
        ("单词记忆", "vocab", 440),
        ("笔记记录", "note", 570),
        ("专注计时", "timer", 700),
        ("导入设置", "import/settings", 65),
    ]
    for name, route, x in features:
        y = 310
        w = 110 if len(name) <= 4 else 115
        rect(d, x, y, w, 40, fill=WHITE, outline=BORDER)
        text(d, x + w // 2, y + 20, name, font_small, BLACK, anchor='mm')

    # 底部
    rect(d, 250, 390, 350, 45, fill=(240, 255, 240), outline=GREEN)
    text(d, 425, 412, "所有页面响应式适配 电脑/平板/手机", font_normal, GREEN, anchor='mm')

    text(d, 425, 470, "共 20+ 个页面 | 11 个路由模块 | 47 个模板文件", font_small, GRAY, anchor='mt')

    img.save(os.path.join(OUT_DIR, "04_页面导航图.png"))
    print("04_页面导航图.png OK")


# ============ 5. 功能模块结构图 ============
def draw_modules():
    img = new_img(850, 350, LIGHT)
    d = ImageDraw.Draw(img)

    text(d, 425, 25, "系统功能模块结构图", font_title, BLACK, anchor='mt')

    rect(d, 300, 55, 250, 45, fill=(255, 248, 230), outline=GOLD)
    text(d, 425, 77, "考研一体化学习辅助系统", font_bold, BLACK, anchor='mm')

    arrow_down(d, 425, 105, GRAY)

    modules = [
        ("用户系统", "注册/登录/游客", GOLD),
        ("题目管理", "录入/列表/详情", CORAL),
        ("做题练习", "随机/选题/判分", GREEN),
        ("错题追踪", "自动收集/曲线复习", RED),
        ("单词记忆", "卡片学习/回炉/复习", BLUE),
        ("笔记记录", "富文本/分类/置顶", PURPLE),
        ("专注计时", "番茄钟/记录/统计", GREEN),
        ("批量导入", "粘贴解析/Excel", CORAL),
    ]

    for i, (name, desc, color) in enumerate(modules):
        x = 30 + i * 100
        rect(d, x, 140, 90, 35, fill=WHITE, outline=color)
        text(d, x + 45, 150, name, font_small, color, anchor='mt')
        text(d, x + 45, 165, desc, font_small, GRAY, anchor='mt')

    # 底部功能
    bot = [
        ("学习仪表盘", "统计/倒计时/语录", 100),
        ("管理后台", "Hero图/图库/科目", 290),
        ("系统设置", "图片上传/科目管理", 480),
        ("学习统计", "Chart.js图表", 670),
    ]
    for name, desc, x in bot:
        rect(d, x, 210, 140, 40, fill=WHITE, outline=BORDER)
        text(d, x + 70, 222, name, font_small, BLACK, anchor='mt')
        text(d, x + 70, 240, desc, font_small, GRAY, anchor='mt')

    rect(d, 100, 280, 650, 35, fill=(240, 248, 255), outline=BLUE)
    text(d, 425, 297, "全部模块通过导航栏 + 仪表盘快捷入口串联，形成完整学习工作流", font_small, BLUE, anchor='mm')

    img.save(os.path.join(OUT_DIR, "05_功能模块结构图.png"))
    print("05_功能模块结构图.png OK")


# ============ 6. 单词学习流程图 ============
def draw_vocab_flow():
    img = new_img(700, 450, LIGHT)
    d = ImageDraw.Draw(img)

    text(d, 350, 20, "单词学习 — 回炉循环流程", font_title, BLACK, anchor='mt')

    # 新词池
    rect(d, 250, 55, 200, 45, fill=(240, 248, 255), outline=BLUE)
    text(d, 350, 77, "新词池 (stage=-1)", font_bold, BLACK, anchor='mm')
    arrow_down(d, 350, 105, BLUE)

    # 学习卡片
    rect(d, 200, 130, 300, 60, fill=WHITE, outline=GOLD)
    text(d, 350, 150, "📝 学习卡片 (显示单词+释义)", font_bold, BLACK, anchor='mt')
    text(d, 350, 172, "「认识」/「不认识」", font_small, GRAY, anchor='mt')

    # 分支
    arrow_down(d, 280, 195, GREEN)
    arrow_down(d, 420, 195, RED)
    text(d, 265, 210, "认识 ✓", font_small, GREEN, anchor='mt')
    text(d, 435, 210, "不认识 ✗", font_small, RED, anchor='mt')

    # 认识
    rect(d, 150, 230, 180, 45, fill=(240, 255, 240), outline=GREEN)
    text(d, 240, 245, "进入复习周期", font_bold, GREEN, anchor='mm')
    text(d, 240, 262, "stage=0, 1天后复习", font_small, GRAY, anchor='mt')

    # 不认识
    rect(d, 380, 230, 180, 45, fill=(255, 240, 240), outline=RED)
    text(d, 470, 245, "加入回炉队列", font_bold, RED, anchor='mm')
    text(d, 470, 262, "保持 stage=-1", font_small, GRAY, anchor='mt')

    # 回炉
    arrow_down(d, 470, 280, RED)
    rect(d, 300, 310, 340, 55, fill=(255, 248, 230), outline=GOLD)
    text(d, 470, 328, "本轮全部过完 → 回炉词重新出现", font_bold, BLACK, anchor='mt')
    text(d, 470, 348, "循环直到所有词都点「认识」", font_small, GRAY, anchor='mt')

    # 完成
    arrow_down(d, 350, 370, GREEN)
    rect(d, 230, 390, 240, 40, fill=(240, 255, 240), outline=GREEN)
    text(d, 350, 410, "🎉 全部认识！学习完成", font_bold, GREEN, anchor='mm')

    img.save(os.path.join(OUT_DIR, "06_单词学习流程图.png"))
    print("06_单词学习流程图.png OK")


if __name__ == "__main__":
    draw_architecture()
    draw_er()
    draw_memory_curve()
    draw_navigation()
    draw_modules()
    draw_vocab_flow()
    print(f" 全部图片生成完毕 → {OUT_DIR}")
