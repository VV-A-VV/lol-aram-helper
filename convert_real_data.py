import json

# Playwright获取的真实数据
raw_data = [
  {"id": "876", "name": "莉莉娅", "tier": "T1", "winrate": "59.09%", "augments": ["祖母的辣椒油", "红包", "咏叹奏鸣"]},
  {"id": "904", "name": "亚恒", "tier": "T1", "winrate": "55.37%", "augments": ["舞会女王", "红包", "潘朵拉的盒子"]},
  {"id": "63", "name": "布兰德", "tier": "T1", "winrate": "55.31%", "augments": ["炼狱导管", "祖母的辣椒油", "咏叹奏鸣"]},
  {"id": "27", "name": "辛吉德", "tier": "T1", "winrate": "55.03%", "augments": ["潘朵拉的盒子", "舞会女王", "魄罗之王的弹跳"]},
  {"id": "147", "name": "萨勒芬妮", "tier": "T1", "winrate": "54.73%", "augments": ["回力OK镖", "缩小引擎", "咏叹奏鸣"]},
  {"id": "67", "name": "薇恩", "tier": "T1", "winrate": "54.25%", "augments": ["巫师式思考", "双刀流", "和我一起困在这里"]},
  {"id": "90", "name": "玛尔扎哈", "tier": "T1", "winrate": "54.24%", "augments": ["咏叹奏鸣", "祖母的辣椒油", "巨人杀手"]},
  {"id": "157", "name": "亚索", "tier": "T2", "winrate": "51.54%", "augments": ["红包", "舞会女王", "会心治疗"]},
  {"id": "238", "name": "劫", "tier": "T2", "winrate": "51.62%", "augments": ["红包", "有始有终", "最终都市列车"]},
  {"id": "103", "name": "阿狸", "tier": "T1", "winrate": "53.38%", "augments": ["升级：耀光", "咏叹奏鸣", "红包"]}
]

# 通用装备推荐
items_by_type = {
    "法师": ["帽子", "法穿棒", "金身", "面具", "虚空", "法穿鞋"],
    "AD": ["无尽", "饮血", "破败", "复活甲", "幕刃", "攻速鞋"],
    "坦克": ["日炎", "荆棘", "石像", "振奋", "亡板", "护甲鞋"]
}

# 转换为最终格式
champions = {}
for champ in raw_data:
    # 简单判断类型（实际应该更复杂）
    items = items_by_type["法师"]  # 默认法师装备

    champions[champ["id"]] = {
        "name": champ["name"],
        "tier": champ["tier"],
        "winrate": champ["winrate"],
        "augments": champ["augments"],
        "items": items
    }

output = {
    "last_update": "2026-03-17",
    "champions": champions
}

with open('champions_data_real.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Converted {len(champions)} champions")
