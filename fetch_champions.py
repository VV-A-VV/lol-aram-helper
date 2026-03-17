#!/usr/bin/env python3
"""自动从 hextech.dtodo.cn 抓取所有英雄数据"""
import json
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def fetch_champions():
    url = "https://hextech.dtodo.cn/zh-CN"
    print(f"正在访问 {url}...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.select('table tbody tr')

    champions = {}
    for row in rows:
        cells = row.select('td')
        if len(cells) >= 6:
            link = cells[1].select_one('a')
            if link and 'href' in link.attrs:
                match = re.search(r'champion-stats/(\d+)', link['href'])
                if match:
                    champ_id = match.group(1)
                    name = cells[1].get_text(strip=True).split('\n')[0].replace('攻略', '').strip()
                    tier = cells[2].get_text(strip=True)
                    winrate = cells[3].get_text(strip=True)

                    augment_links = cells[5].select('a')
                    augments = []
                    for a in augment_links[:3]:
                        img = a.select_one('img')
                        augments.append(img['alt'] if img and 'alt' in img.attrs else a.get_text(strip=True))

                    champions[champ_id] = {
                        'name': name,
                        'tier': tier,
                        'winrate': winrate,
                        'augments': augments
                    }

    data = {
        'last_update': datetime.now().strftime('%Y-%m-%d'),
        'champions': champions
    }

    with open('champions_raw.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] 成功抓取 {len(champions)} 个英雄")
    print(f"[OK] 保存到 champions_raw.json")
    return len(champions)

if __name__ == "__main__":
    try:
        count = fetch_champions()
        print(f"\n下一步: python auto_update.py")
    except Exception as e:
        print(f"[ERROR] 抓取失败: {e}")
