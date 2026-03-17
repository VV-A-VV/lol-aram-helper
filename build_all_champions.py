#!/usr/bin/env python3
import json

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

def get_items(name):
    for type_name, champ_list in config['champion_types'].items():
        if any(x in name for x in champ_list):
            return config['item_recommendations'][type_name]
    return config['item_recommendations']['ad']

# 所有英雄数据将在下面添加
all_champions = {}
