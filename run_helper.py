#!/usr/bin/env python3
"""LOL ARAM Helper 启动器"""
import os
import sys
import subprocess

def main():
    if not os.path.exists('champions_data.json'):
        print("[ERROR] 未找到 champions_data.json")
        print("\n首次设置:")
        print("1. 使用浏览器脚本提取数据 (见 SETUP.md)")
        print("2. python auto_update.py")
        print("3. python run_helper.py")
        sys.exit(1)

    print("[OK] 启动 LOL ARAM Helper...")
    subprocess.run([sys.executable, 'floating_window.py'])

if __name__ == "__main__":
    main()
