# 路由/API 设计

## 页面路由（服务端渲染）

### 公开页面（无需登录）

| 方法 | 路由 | 说明 | 模板 |
|------|------|------|------|
| GET | `/` | 首页 | `index.html` |
| GET/POST | `/auth/login` | 登录 | `auth/login.html` |
| GET/POST | `/auth/register` | 注册 | `auth/register.html` |

### 需登录页面

| 方法 | 路由 | 说明 | 模板 |
|------|------|------|------|
| GET | `/dashboard` | 学习仪表盘 | `dashboard.html` |
| GET | `/exam` | 题目列表 | `exam/list.html` |
| GET | `/exam/<id>` | 做题 | `exam/practice.html` |
| GET/POST | `/exam/create` | 录入题目 | `exam/create.html` |
| GET/POST | `/exam/<id>/edit` | 编辑题目 | `exam/edit.html` |
| GET | `/workbook` | 习题册列表 | `exam/workbook_list.html` |
| GET/POST | `/workbook/create` | 创建习题册 | `exam/workbook_create.html` |
| GET | `/workbook/<id>` | 习题册详情 | `exam/workbook_detail.html` |
| GET | `/mistake` | 错题本 | `mistake/list.html` |
| GET | `/mistake/review` | 错题复习 | `mistake/review.html` |
| GET | `/vocab` | 单词本 | `vocab/list.html` |
| GET | `/vocab/review` | 单词复习 | `vocab/review.html` |
| GET/POST | `/vocab/add` | 添加单词 | `vocab/add.html` |
| GET | `/note` | 笔记列表 | `note/list.html` |
| GET/POST | `/note/create` | 写笔记 | `note/edit.html` |
| GET/POST | `/note/<id>/edit` | 编辑笔记 | `note/edit.html` |
| GET | `/timer` | 番茄钟 | `timer/pomodoro.html` |
| GET/POST | `/import` | 批量导入 | `import/index.html` |
| GET | `/user/profile` | 个人中心 | `user/profile.html` |
| GET | `/user/stats` | 学习统计 | `user/stats.html` |

## JSON API（前端 AJAX 调用）

### 做题相关

| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/exam/<id>/submit` | 提交答案，返回对错+解析 |
| POST | `/api/mistake/<id>/review` | 提交错题复习结果 |

### 单词相关

| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/vocab/<id>/review` | 提交单词自评结果 |
| POST | `/api/vocab/batch-add` | 批量添加单词 |

### 计时相关

| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/timer/record` | 记录学习时段 |
| GET | `/api/user/stats` | 获取统计数据(JSON) |

### 导入相关

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/api/import/template/exam` | 下载真题导入模板 |
| GET | `/api/import/template/vocab` | 下载单词导入模板 |
| POST | `/api/import/upload` | 上传并处理导入文件 |

### 图片上传

| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/upload/image` | 粘贴/拖拽图片上传 |
