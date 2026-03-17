#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import json
import base64
import urllib.request
import ssl
import re
import threading
import time
import sys
import os
from datetime import datetime
import psutil

# Color scheme
COLORS = {
    'bg': '#1a1a2e',
    'card_bg': '#16213e',
    'card_selected': '#0f3460',
    'tier_t1': '#FFD700',
    'tier_t2': '#C0C0C0',
    'tier_t3': '#CD7F32',
    'border_selected': '#00D9FF',
    'text_primary': '#FFFFFF',
    'text_secondary': '#94A3B8',
    'text_muted': '#64748B'
}

class ChampionCard(tk.Frame):
    def __init__(self, parent, champion_data, is_selected=False):
        super().__init__(parent, bg=COLORS['card_selected'] if is_selected else COLORS['card_bg'])
        self.configure(relief='solid', borderwidth=2 if is_selected else 1,
                      highlightbackground=COLORS['border_selected'] if is_selected else COLORS['card_bg'],
                      highlightthickness=2 if is_selected else 0)

        # Main container with padding
        container = tk.Frame(self, bg=self['bg'])
        container.pack(fill='both', expand=True, padx=8, pady=6)

        # Top row: name, tier, winrate
        top_row = tk.Frame(container, bg=self['bg'])
        top_row.pack(fill='x')

        # Selection indicator
        if is_selected:
            indicator = tk.Label(top_row, text=">>", fg=COLORS['border_selected'],
                               bg=self['bg'], font=('Consolas', 12, 'bold'))
            indicator.pack(side='left', padx=(0, 4))

        # Champion name
        name = tk.Label(top_row, text=champion_data.get('name', 'Unknown'),
                       fg=COLORS['text_primary'], bg=self['bg'],
                       font=('Microsoft YaHei UI', 11, 'bold'))
        name.pack(side='left')

        # Tier badge
        tier = champion_data.get('tier', '?')
        tier_color = COLORS.get(f'tier_{tier.lower()}', COLORS['text_secondary'])
        tier_label = tk.Label(top_row, text=f"[{tier}]",
                            fg=tier_color, bg=self['bg'],
                            font=('Consolas', 10, 'bold'))
        tier_label.pack(side='left', padx=(6, 4))

        # Winrate
        wr = champion_data.get('winrate', '?')
        wr_label = tk.Label(top_row, text=wr,
                          fg=COLORS['text_secondary'], bg=self['bg'],
                          font=('Consolas', 10))
        wr_label.pack(side='left')

        # Augments row
        augs = champion_data.get('augments', [])
        if augs:
            aug_row = tk.Frame(container, bg=self['bg'])
            aug_row.pack(fill='x', pady=(4, 0))
            aug_label = tk.Label(aug_row, text=' / '.join(augs),
                               fg=COLORS['text_muted'], bg=self['bg'],
                               font=('Microsoft YaHei UI', 9))
            aug_label.pack(anchor='w')

        # Items row
        items = champion_data.get('items', [])
        if items:
            item_row = tk.Frame(container, bg=self['bg'])
            item_row.pack(fill='x', pady=(2, 0))
            item_label = tk.Label(item_row, text=' > '.join(items[:3]),
                                fg=COLORS['text_primary'], bg=self['bg'],
                                font=('Microsoft YaHei UI', 9))
            item_label.pack(anchor='w')

class FloatingWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LOL ARAM Helper")
        self.root.attributes('-topmost', True)
        self.root.geometry('520x650+50+50')
        self.root.configure(bg=COLORS['bg'])

        # Status bar
        self.status_bar = tk.Frame(self.root, bg=COLORS['card_bg'], height=35)
        self.status_bar.pack(fill='x', padx=5, pady=(5, 0))
        self.status_bar.pack_propagate(False)

        self.status_label = tk.Label(self.status_bar, text="状态: 连接中...",
                                     fg=COLORS['text_secondary'], bg=COLORS['card_bg'],
                                     font=('Microsoft YaHei UI', 9))
        self.status_label.pack(side='left', padx=10, pady=8)

        # Update button
        self.update_btn = tk.Button(self.status_bar, text="更新数据",
                                    command=self.update_data,
                                    bg=COLORS['card_selected'], fg=COLORS['text_primary'],
                                    font=('Microsoft YaHei UI', 9), relief='flat',
                                    cursor='hand2', padx=10)
        self.update_btn.pack(side='right', padx=10, pady=6)

        # Scrollable canvas container
        canvas_frame = tk.Frame(self.root, bg=COLORS['bg'])
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS['bg'])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill='both', expand=True)

        self.port = None
        self.token = None
        self.data = self.load_data()
        self.cards = []
        threading.Thread(target=self.monitor, daemon=True).start()

    def load_data(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            data_file = os.path.join(base_path, 'champions_data.json')
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'champions': {}}

    def connect_lcu(self):
        try:
            for proc in psutil.process_iter(['name', 'cmdline']):
                if 'LeagueClientUx' in proc.info['name']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    port = re.search(r'--app-port=(\d+)', cmdline)
                    token = re.search(r'--remoting-auth-token=([\w-]+)', cmdline)
                    if port and token:
                        self.port = port.group(1)
                        self.token = token.group(1)
                        return True
        except:
            pass
        return False

    def get_session(self):
        if not self.port:
            return None
        url = f'https://127.0.0.1:{self.port}/lol-champ-select/v1/session'
        auth = base64.b64encode(f'riot:{self.token}'.encode()).decode()
        req = urllib.request.Request(url, headers={'Authorization': f'Basic {auth}'})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=2) as res:
                return json.loads(res.read())
        except:
            return None

    def clear_cards(self):
        for card in self.cards:
            card.destroy()
        self.cards = []

    def update_status(self, text):
        self.status_label.config(text=text)

    def fetch_data_from_web(self):
        """从网络获取最新数据"""
        try:
            url = "https://hextech.dtodo.cn/zh-CN"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8')

            # 提取表格内容
            tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', html, re.DOTALL)
            if not tbody_match:
                return False

            tbody = tbody_match.group(1)
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody, re.DOTALL)

            champions = {}
            for row in rows:
                champ_id_match = re.search(r'champion-stats/(\d+)', row)
                if not champ_id_match:
                    continue

                champ_id = champ_id_match.group(1)
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)

                if len(cells) >= 6:
                    # 英雄名
                    name_match = re.search(r'>([^<]+)</a>', cells[1])
                    name = name_match.group(1).strip() if name_match else f'ID:{champ_id}'

                    # 评级
                    tier_cell = re.sub(r'<!--.*?-->', '', cells[2])
                    tier_match = re.search(r'T(\d)', tier_cell)
                    tier = f'T{tier_match.group(1)}' if tier_match else '?'

                    # 胜率
                    wr_match = re.search(r'>(\d+\.\d+%)<', cells[3])
                    wr = wr_match.group(1) if wr_match else '?'

                    # 符文（第6列）
                    augments = []
                    aug_matches = re.findall(r'alt="([^"]+)"', cells[5])
                    if aug_matches:
                        augments = aug_matches[:3]

                    # 装备：从现有数据保留
                    existing = self.data['champions'].get(champ_id, {})
                    items = existing.get('items', [])

                    champions[champ_id] = {
                        'name': name,
                        'tier': tier,
                        'winrate': wr,
                        'augments': augments,
                        'items': items
                    }

            if champions:
                from datetime import datetime
                data = {
                    'last_update': datetime.now().strftime('%Y-%m-%d'),
                    'champions': champions
                }
                with open('champions_data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True
            return False
        except:
            return False

    def update_data(self):
        def run_update():
            self.update_btn.config(state='disabled', text='更新中...')
            try:
                if self.fetch_data_from_web():
                    self.data = self.load_data()
                    self.update_btn.config(text='更新成功', bg='#10b981')
                else:
                    self.update_btn.config(text='更新失败', bg='#ef4444')
            except:
                self.update_btn.config(text='更新失败', bg='#ef4444')
            finally:
                self.root.after(2000, lambda: self.update_btn.config(
                    state='normal', text='更新数据', bg=COLORS['card_selected']))

        threading.Thread(target=run_update, daemon=True).start()

    def monitor(self):
        while True:
            if not self.port:
                if self.connect_lcu():
                    self.update_status("状态: 已连接")
                else:
                    self.update_status("状态: 未检测到客户端")
                    self.clear_cards()
            else:
                session = self.get_session()
                if session:
                    # 获取已选中的英雄
                    selected_id = 0
                    try:
                        for ag in session.get('actions', []):
                            for a in ag:
                                if a.get('actorCellId') == session.get('localPlayerCellId') and a.get('championId'):
                                    selected_id = a['championId']
                    except:
                        pass

                    # 获取可交换的英雄
                    bench = session.get('benchChampions', [])
                    bench_ids = [c['championId'] for c in bench]

                    # 合并所有英雄
                    all_ids = [selected_id] + bench_ids if selected_id else bench_ids

                    if all_ids:
                        champ_count = len(self.data['champions'])
                        self.update_status(f"状态: 已连接 | {champ_count} 英雄")

                        # Clear old cards
                        self.clear_cards()

                        # Create new cards
                        for cid in all_ids:
                            champ = self.data['champions'].get(str(cid), {})
                            if not champ.get('name'):
                                champ['name'] = f'ID:{cid}'

                            card = ChampionCard(self.scrollable_frame, champ, is_selected=(cid == selected_id))
                            card.pack(fill='x', pady=3)
                            self.cards.append(card)
                    else:
                        self.update_status("状态: 等待选人...")
                        self.clear_cards()
                else:
                    self.update_status("状态: 等待进入选人...")
                    self.clear_cards()
            time.sleep(2)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    FloatingWindow().run()
