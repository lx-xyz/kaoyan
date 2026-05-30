@echo off
chcp 65001 >nul
echo 正在安装 Python 依赖包...
cd /d "%~dp0"
pip install -r requirements.txt
echo.
echo 安装完成！按任意键退出。
pause >nul
