#!/usr/bin/env python3
import urllib.request
import json
import re

url = 'https://op.gg/zh-cn/lol/modes/aram'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, timeout=10) as res:
        html = res.read().decode('utf-8')

    # 保存HTML用于分析
    with open('opgg_aram.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("HTML saved to opgg_aram.html")
    print(f"Size: {len(html)} bytes")

    # 尝试提取JSON数据
    json_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if json_match:
        data = json.loads(json_match.group(1))
        with open('opgg_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("JSON data saved to opgg_data.json")
    else:
        print("No JSON data found")

except Exception as e:
    print(f"Error: {e}")
