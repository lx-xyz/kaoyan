import sys, os, shutil

# PyInstaller打包的exe首次运行时自动初始化数据库
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    os.makedirs(os.path.join(exe_dir, 'data'), exist_ok=True)
    os.makedirs(os.path.join(exe_dir, 'uploads'), exist_ok=True)
    db_target = os.path.join(exe_dir, 'data', 'kaoyan.db')
    if not os.path.exists(db_target):
        db_source = os.path.join(sys._MEIPASS, 'data', 'kaoyan.db')
        if os.path.exists(db_source):
            shutil.copy2(db_source, db_target)

from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False, host="127.0.0.1", port=5000)

