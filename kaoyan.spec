# -*- mode: python ; coding: utf-8 -*-
import os
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集所有需要打包的数据文件
datas = [
    ('app/templates', 'app/templates'),
    ('app/static', 'app/static'),
    ('migrations', 'migrations'),
    ('scripts', 'scripts'),
    ('config.py', '.'),
    ('data/kaoyan.db', 'data'),
    ('uploads', 'uploads'),
]

# 创建data目录（PyInstaller无法打包空目录，在代码里自动创建）

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'app', 'app.routes', 'app.routes.main', 'app.routes.auth',
        'app.routes.exam', 'app.routes.mistake', 'app.routes.vocab',
        'app.routes.note', 'app.routes.timer', 'app.routes.import_data',
        'app.routes.quick_input', 'app.routes.settings', 'app.routes.admin',
        'app.routes.user', 'app.services', 'app.services.spaced_repetition',
        'flask', 'flask_sqlalchemy', 'flask_login', 'flask_bcrypt',
        'flask_wtf', 'flask_migrate', 'sqlalchemy', 'wtforms',
        'pandas', 'openpyxl', 'PIL', 'werkzeug', 'jinja2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'numpy.testing'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='考研学习系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
