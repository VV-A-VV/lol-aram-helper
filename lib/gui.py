#!/usr/bin/env python3
"""
GUI 界面 - 实时显示英雄信息
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from lcu_connector import LCUConnector

class AramHelper:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("LOL 海克斯大乱斗助手")
        self.window.geometry("500x400")

        self.connector = LCUConnector()
        self.running = True

        self._create_ui()
        self._start_monitor()

    def _create_ui(self):
        # 状态标签
        self.status_label = tk.Label(
            self.window,
            text="正在连接客户端...",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=20)

        # 英雄信息框
        self.info_frame = ttk.Frame(self.window)
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.info_text = tk.Text(
            self.info_frame,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)

    def _start_monitor(self):
        def monitor():
            while self.running:
                self._update_data()
                time.sleep(2)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def _update_data(self):
        if not self.connector.base_url:
            self.status_label.config(text="❌ 客户端未运行")
            return

        session = self.connector.get_champ_select_session()

        if 'error' in session or 'httpStatus' in session:
            self.status_label.config(text="⚠️ 不在选英雄阶段")
            self.info_text.delete(1.0, tk.END)
            return

        self.status_label.config(text="✅ 已连接")
        self._display_champions(session)

    def _display_champions(self, session):
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "当前可选英雄信息\n")
        self.info_text.insert(tk.END, "=" * 50 + "\n\n")

        # 这里可以添加更多解析逻辑
        self.info_text.insert(tk.END, "请访问 op.gg 查看详细数据\n")

    def run(self):
        self.window.mainloop()
        self.running = False

if __name__ == '__main__':
    app = AramHelper()
    app.run()
