#!/usr/bin/env python3
"""
合并所有英雄数据并添加装备推荐
"""
import json

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

def get_items(name):
    for type_name, champ_list in config['champion_types'].items():
        if any(x in name for x in champ_list):
            return config['item_recommendations'][type_name]
    return config['item_recommendations']['ad']

# 第1批数据 (43个)
batch1_json = '''{"1":{"name":"黑暗之女 安妮","tier":"T2","winrate":"51.16%","augments":["祖母的辣椒油","红包","咏叹奏鸣"]},"2":{"name":"狂战士 奥拉夫","tier":"T3","winrate":"48.88%","augments":["男爵之手","红包","舞会女王"]},"3":{"name":"正义巨像 加里奥","tier":"T1","winrate":"53.44%","augments":["任务：艾卡西亚的陷落","缩小引擎","升级：荆棘之甲"]}}'''

# 第2批数据 (43个) - 将在下一个文件中定义
# 第3批数据 (43个) - 将在下一个文件中定义
# 第4批数据 (43个) - 将在下一个文件中定义

print("请运行 build_complete_data_part2.py 来完成数据构建")
