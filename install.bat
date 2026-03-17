@echo off
echo ========================================
echo LOL 海克斯大乱斗助手 - 安装程序
echo ========================================
echo.

echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未安装 Python
    echo 请从 https://www.python.org 下载安装
    pause
    exit /b 1
)
echo ✓ Python 已安装

echo.
echo [2/3] 安装依赖...
pip install psutil
if errorlevel 1 (
    echo 警告: 依赖安装失败
)

echo.
echo [3/3] 安装完成！
echo.
echo 使用方法:
echo   1. 启动英雄联盟客户端
echo   2. 进入海克斯大乱斗选英雄界面
echo   3. 运行: python lib\main.py
echo   或运行: python lib\gui.py (图形界面)
echo.
pause
