#!/usr/bin/env python3
"""
英雄联盟海克斯大乱斗数据抓取工具
从 op.gg 获取英雄数据
"""

import sys
import json
import urllib.request
from html.parser import HTMLParser

# 英雄名称映射
CHAMPION_MAP = {
    '奎因': 'quinn', '亚索': 'yasuo', '劫': 'zed', '阿狸': 'ahri',
    '盖伦': 'garen', '拉克丝': 'lux', '金克斯': 'jinx', '卡特琳娜': 'katarina',
    '提莫': 'teemo', '薇恩': 'vayne', '德莱文': 'draven', '伊泽瑞尔': 'ezreal'
}

def get_champion_data(champion_name):
    """获取英雄数据"""
    english_name = CHAMPION_MAP.get(champion_name, champion_name.lower())
    url = f'https://op.gg/zh-cn/lol/modes/aram-mayhem/{english_name}/build'

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            return parse_data(html, champion_name, url)
    except Exception as e:
        return {'error': str(e), 'champion': champion_name, 'url': url}

def parse_data(html, champion_name, url):
    """解析 HTML 数据"""
    return {
        'champion': champion_name,
        'url': url,
        'message': '请访问上述链接查看详细数据',
        'tip': '由于 op.gg 使用动态加载，建议直接访问网站获取最准确的信息'
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python scraper.py <英雄名称>')
        sys.exit(1)

    result = get_champion_data(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
