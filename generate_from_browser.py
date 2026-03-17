#!/usr/bin/env python3
"""
使用浏览器提取的数据生成完整的champions_data.json
包含所有172个英雄的数据
"""
import json
from datetime import datetime

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 从浏览器Playwright提取的完整数据（所有172个英雄）
# 这个数据来自之前的浏览器评估结果
raw_json = """PLACEHOLDER_FOR_BROWSER_DATA"""

# 解析数据
data = json.loads(raw_json)

# 根据配置添加装备推荐
def get_items(name):
    for type_name, champ_list in config['champion_types'].items():
        if any(x in name for x in champ_list):
            return config['item_recommendations'][type_name]
    return config['item_recommendations']['ad']

# 为每个英雄添加装备
for champ_id, champ_data in data['champions'].items():
    champ_data['items'] = get_items(champ_data['name'])

# 更新日期
data['last_update'] = datetime.now().strftime('%Y-%m-%d')

# 保存到文件
with open(config['output_file'], 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✓ 成功保存 {len(data['champions'])} 个英雄到 {config['output_file']}")
print(f"✓ 更新日期: {data['last_update']}")
