#!/usr/bin/env python3
"""
自动更新脚本 - 从hextech.dtodo.cn获取最新数据
运行: python auto_update.py
"""
import json
import os
from datetime import datetime

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_items(name, config):
    """根据英雄名称返回推荐装备"""
    for type_name, champ_list in config['champion_types'].items():
        if any(x in name for x in champ_list):
            return config['item_recommendations'][type_name]
    return config['item_recommendations']['ad']

def main():
    config = load_config()

    # 读取浏览器提取的原始数据
    # 这个文件应该由浏览器脚本生成
    raw_file = 'champions_raw.json'

    if not os.path.exists(raw_file):
        print(f"错误: 未找到 {raw_file}")
        print("请先运行浏览器脚本获取数据")
        return

    with open(raw_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 添加装备推荐
    for champ_id, champ_data in data['champions'].items():
        champ_data['items'] = get_items(champ_data['name'], config)

    # 更新日期
    data['last_update'] = datetime.now().strftime('%Y-%m-%d')

    # 保存
    with open(config['output_file'], 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] 成功更新 {len(data['champions'])} 个英雄")
    print(f"[OK] 保存到: {config['output_file']}")
    print(f"[OK] 更新时间: {data['last_update']}")

    # 验证关键英雄
    test_ids = ['112', '203', '233']
    for cid in test_ids:
        if cid in data['champions']:
            print(f"[OK] 验证: {data['champions'][cid]['name']}")

if __name__ == "__main__":
    main()
