from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

login_manager.login_view = "main.index"
login_manager.login_message = None


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.exam import exam_bp
    from app.routes.mistake import mistake_bp
    from app.routes.vocab import vocab_bp
    from app.routes.note import note_bp
    from app.routes.timer import timer_bp
    from app.routes.import_data import import_bp
    from app.routes.quick_input import quick_bp
    from app.routes.settings import settings_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(exam_bp)
    app.register_blueprint(mistake_bp)
    app.register_blueprint(vocab_bp)
    app.register_blueprint(note_bp)
    app.register_blueprint(timer_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(quick_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)

    # 上传文件路由：exe运行时文件在外部目录
    from flask import send_from_directory
    upload_dir = app.config['UPLOAD_FOLDER']
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        import os as _os
        return send_from_directory(upload_dir, filename)

    return app


from app import models  # noqa: E402 — 确保模型被导入以便 flask db 检测
