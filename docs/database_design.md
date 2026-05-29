# 数据库表设计

## ER 关系概览

```
User (1) ──< (N) ExamRecord       # 用户做题记录
User (1) ──< (N) MistakeItem      # 用户错题
User (1) ──< (N) VocabularyWord   # 用户单词
User (1) ──< (N) Note             # 用户笔记
User (1) ──< (N) StudySession     # 用户学习时段
User (1) ──< (N) Workbook         # 用户自定义习题册

Subject (1) ──< (N) ExamQuestion  # 科目下题目
Subject (1) ──< (N) Workbook      # 科目下习题册

Workbook (1) ──< (N) WorkbookQuestion  # 习题册包含的题目
ExamQuestion (1) ──< (N) WorkbookQuestion
```

---

## 表定义

### 1. user（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, 自增 | 用户ID |
| username | String(64) | UNIQUE, NOT NULL | 用户名 |
| email | String(128) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | String(256) | NOT NULL | bcrypt 密码哈希 |
| nickname | String(64) | nullable | 昵称 |
| target_school | String(128) | nullable | 目标院校 |
| target_major | String(128) | nullable | 目标专业 |
| daily_goal_hours | Integer | default=4 | 每日学习目标(小时) |
| is_admin | Boolean | default=False | 管理员标记 |
| created_at | DateTime | default=now | 注册时间 |
| last_login | DateTime | nullable | 最后登录时间 |

### 2. subject（科目表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, 自增 | 科目ID |
| name | String(64) | UNIQUE, NOT NULL | 科目名称 |
| code | String(16) | UNIQUE, NOT NULL | 科目代号 |
| color | String(7) | nullable | 科目代表色 |
| sort_order | Integer | default=0 | 排序 |

**预置数据**：英语二(english/#FF6B6B)、数学二(math/#4ECDC4)、408计算机综合(cs/#45B7D1)

### 3. exam_question（题目表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 题目ID |
| subject_id | FK→subject.id | 所属科目 |
| year | Integer, nullable | 年份 |
| source | String(128) | 来源 |
| question_type | String(32) | 题型 |
| question_number | Integer, nullable | 题号 |
| title | Text | 题干(Markdown) |
| option_a | Text, nullable | 选项A |
| option_b | Text, nullable | 选项B |
| option_c | Text, nullable | 选项C |
| option_d | Text, nullable | 选项D |
| correct_answer | String(256) | 正确答案 |
| analysis | Text, nullable | 解析 |
| difficulty | Integer, default=3 | 难度1~5 |
| tags | String(256), nullable | 标签 |
| created_by | FK→user.id, nullable | 录入者 |
| is_public | Boolean, default=True | 是否公开 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 4. workbook（习题册表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 习题册ID |
| title | String(128) | 名称 |
| description | Text, nullable | 描述 |
| subject_id | FK→subject.id | 科目 |
| user_id | FK→user.id | 创建者 |
| is_public | Boolean, default=False | 是否公开 |
| question_count | Integer, default=0 | 题目数(冗余) |
| created_at | DateTime | 创建时间 |

### 5. workbook_question（习题册-题目关联）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 关联ID |
| workbook_id | FK→workbook.id | 习题册 |
| question_id | FK→exam_question.id | 题目 |
| sort_order | Integer | 排序 |

### 6. exam_record（做题记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 记录ID |
| user_id | FK→user.id | 用户 |
| question_id | FK→exam_question.id | 题目 |
| user_answer | String(256) | 用户答案 |
| is_correct | Boolean | 是否正确 |
| duration_seconds | Integer, nullable | 耗时(秒) |
| session_type | String(16), default='practice' | 模式 |
| created_at | DateTime | 做题时间 |

### 7. mistake_item（错题本）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 错题ID |
| user_id | FK→user.id | 用户 |
| question_id | FK→exam_question.id | 题目 |
| wrong_count | Integer, default=1 | 错误次数 |
| last_wrong_at | DateTime | 最后错误时间 |
| last_review_at | DateTime, nullable | 最近复习时间 |
| next_review_at | DateTime, nullable | 下次复习时间 |
| mastery_level | Integer, default=0 | 掌握度0~5 |
| note | Text, nullable | 用户备注 |
| status | String(16), default='active' | active/mastered/archived |

### 8. vocabulary_word（单词表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 单词ID |
| user_id | FK→user.id | 用户 |
| word | String(128) | 单词 |
| phonetic | String(128), nullable | 音标 |
| meaning | Text | 中文释义 |
| example_sentence | Text, nullable | 例句 |
| example_translation | Text, nullable | 例句翻译 |
| part_of_speech | String(32), nullable | 词性 |
| difficulty | Integer, default=3 | 难度 |
| review_stage | Integer, default=0 | 记忆阶段0~5 |
| last_review_at | DateTime, nullable | 最近复习 |
| next_review_at | DateTime, nullable | 下次复习 |
| review_count | Integer, default=0 | 复习次数 |
| is_mastered | Boolean, default=False | 已掌握 |
| created_at | DateTime | 添加时间 |

### 9. note（笔记表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 笔记ID |
| user_id | FK→user.id | 用户 |
| title | String(256) | 标题 |
| content | Text | 内容(Markdown) |
| subject_id | FK→subject.id, nullable | 关联科目 |
| category | String(64), nullable | 分类标签 |
| is_pinned | Boolean, default=False | 置顶 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 10. study_session（学习记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 记录ID |
| user_id | FK→user.id | 用户 |
| subject_id | FK→subject.id, nullable | 科目 |
| start_time | DateTime | 开始时间 |
| end_time | DateTime | 结束时间 |
| duration_minutes | Integer | 时长(分钟) |
| session_type | String(32) | pomodoro/free/manual |

### 11. import_log（导入日志）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 日志ID |
| user_id | FK→user.id | 导入者 |
| import_type | String(32) | exam_question/vocabulary |
| file_name | String(256) | 文件名 |
| total_rows | Integer | 总行数 |
| success_rows | Integer | 成功数 |
| error_rows | Integer | 失败数 |
| error_detail | Text, nullable | 错误详情(JSON) |
| created_at | DateTime | 导入时间 |
