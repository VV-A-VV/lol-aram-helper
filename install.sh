#!/bin/bash

echo "========================================"
echo "LOL 海克斯大乱斗助手 - 安装程序"
echo "========================================"
echo

echo "[1/3] 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未安装 Python3"
    echo "请先安装 Python3"
    exit 1
fi
echo "✅ Python3 已安装"

echo
echo "[2/3] 安装依赖..."
pip3 install psutil

echo
echo "[3/3] 安装完成！"
echo
echo "使用方法:"
echo "  1. 启动英雄联盟客户端"
echo "  2. 进入海克斯大乱斗选英雄界面"
echo "  3. 运行: python3 lib/main.py"
echo "  或运行: python3 lib/gui.py (图形界面)"
echo
