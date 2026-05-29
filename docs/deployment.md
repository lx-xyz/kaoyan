# 部署指南

## 本地开发（当前阶段）

```bash
# 在项目根目录下
cd 考研学习系统

# 安装依赖（仅首次）
pip install -r requirements.txt

# 启动开发服务器
python app.py

# 浏览器访问
http://127.0.0.1:5000
```

---

## 部署到 PythonAnywhere（免费）

### 1. 注册账号
访问 https://www.pythonanywhere.com 注册免费账号

### 2. 上传代码
- 方式A：在 PythonAnywhere 的 Files 页面直接上传 ZIP 包
- 方式B（推荐）：先将代码推送到 GitHub，然后在 Bash 中 `git clone`

### 3. 配置 Web App
1. 打开 Web 标签页 → Add a new web app
2. 选择 Flask → Python 3.11
3. 设置工作目录为项目根目录

### 4. 配置 WSGI 文件
修改 `/var/www/<username>_pythonanywhere_com_wsgi.py`：
```python
import sys
path = '/home/<username>/kaoyan_study_system'
if path not in sys.path:
    sys.path.append(path)
from app import create_app
application = create_app()
```

### 5. 安装依赖
在 PythonAnywhere Bash 中：
```bash
pip install -r requirements.txt
```

### 6. 启动
点击 Web 页面的 Reload 按钮

### 7. 访问
`https://<username>.pythonanywhere.com`

---

## 注意事项
- 免费账号有访问频率限制
- 每3个月需要登录一次保持活跃
- SQLite 数据库够用，不需要额外配置
