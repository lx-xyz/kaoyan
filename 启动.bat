@echo off
chcp 65001 >nul
title 考研学习系统
echo.
echo    ============================
echo    考研一体化学习辅助系统
echo    ============================
echo.
echo    正在启动服务器...
echo    启动后请打开浏览器访问: http://127.0.0.1:5000
echo    按 Ctrl+C 可停止服务器
echo.
cd /d "%~dp0"
python app.py
pause
