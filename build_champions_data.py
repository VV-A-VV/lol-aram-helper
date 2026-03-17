import json

# Champion data extracted from hextech.dtodo.cn
champions_raw = {
    "1": {"name": "黑暗之女 安妮", "tier": "T2", "winrate": "51.16%", "augments": ["祖母的辣椒油", "红包", "咏叹奏鸣"]},
    "2": {"name": "狂战士 奥拉夫", "tier": "T3", "winrate": "48.88%", "augments": ["男爵之手", "红包", "舞会女王"]},
    "3": {"name": "正义巨像 加里奥", "tier": "T1", "winrate": "53.44%", "augments": ["任务：艾卡西亚的陷落", "缩小引擎", "升级：荆棘之甲"]},
    "4": {"name": "卡牌大师 崔斯特", "tier": "T3", "winrate": "50.26%", "augments": ["咏叹奏鸣", "红包", "回归基本功"]},
    "5": {"name": "德邦总管 赵信", "tier": "T3", "winrate": "49.80%", "augments": ["舞会女王", "小丑学院", "红包"]},
    "6": {"name": "无畏战车 厄加特", "tier": "T5", "winrate": "45.34%", "augments": ["亮出你的剑", "升级：荆棘之甲", "红包"]},
    "7": {"name": "诡术妖姬 乐芙兰", "tier": "T5", "winrate": "43.03%", "augments": ["咏叹奏鸣", "最终形态", "无休回复"]},
    "8": {"name": "猩红收割者 弗拉基米尔", "tier": "T5", "winrate": "45.34%", "augments": ["回归基本功", "红包", "回力OK镖"]},
    "9": {"name": "远古恐惧 费德提克", "tier": "T4", "winrate": "47.64%", "augments": ["小丑学院", "咏叹奏鸣", "祖母的辣椒油"]},
    "10": {"name": "正义天使 凯尔", "tier": "T1", "winrate": "53.60%", "augments": ["虚幻武器", "红包", "双刀流"]},
    "11": {"name": "无极剑圣 易", "tier": "T1", "winrate": "52.99%", "augments": ["双发快射", "小丑学院", "双刀流"]},
    "12": {"name": "牛头酋长 阿利斯塔", "tier": "T3", "winrate": "50.01%", "augments": ["任务：艾卡西亚的陷落", "慢炖", "舞会女王"]},
    "13": {"name": "符文法师 瑞兹", "tier": "T2", "winrate": "52.00%", "augments": ["回归基本功", "溢流", "由心及物"]},
    "14": {"name": "亡灵战神 赛恩", "tier": "T3", "winrate": "49.93%", "augments": ["慢炖", "任务：艾卡西亚的陷落", "升级：荆棘之甲"]},
    "15": {"name": "战争女神 希维尔", "tier": "T3", "winrate": "50.71%", "augments": ["红包", "潘朵拉的盒子", "男爵之手"]},
    "16": {"name": "众星之子 索拉卡", "tier": "T3", "winrate": "50.30%", "augments": ["风语者的祝福", "回力OK镖", "升级：米凯尔的祝福"]},
    "17": {"name": "迅捷斥候 提莫", "tier": "T4", "winrate": "48.43%", "augments": ["咏叹奏鸣", "祖母的辣椒油", "红包"]},
    "18": {"name": "麦林炮手 崔丝塔娜", "tier": "T2", "winrate": "52.04%", "augments": ["双刀流", "红包", "亮出你的剑"]},
    "19": {"name": "祖安怒兽 沃里克", "tier": "T4", "winrate": "47.46%", "augments": ["小丑学院", "升级：荆棘之甲", "红包"]},
    "20": {"name": "雪原双子 努努和威朗普", "tier": "T4", "winrate": "47.42%", "augments": ["潘朵拉的盒子", "任务：艾卡西亚的陷落", "咏叹奏鸣"]},
    "21": {"name": "赏金猎人 厄运小姐", "tier": "T3", "winrate": "49.71%", "augments": ["红包", "祖母的辣椒油", "亮出你的剑"]},
    "22": {"name": "寒冰射手 艾希", "tier": "T1", "winrate": "52.78%", "augments": ["升级：无尽之刃", "双刀流", "灵魂虹吸"]},
    "23": {"name": "蛮族之王 泰达米尔", "tier": "T3", "winrate": "50.57%", "augments": ["红包", "双刀流", "最万用的瞄准镜"]},
    "24": {"name": "武器大师 贾克斯", "tier": "T2", "winrate": "51.25%", "augments": ["闪光弹", "舞会女王", "小丑学院"]},
    "25": {"name": "堕落天使 莫甘娜", "tier": "T1", "winrate": "52.69%", "augments": ["缩小引擎", "祖母的辣椒油", "咏叹奏鸣"]},
    "26": {"name": "时光守护者 基兰", "tier": "T3", "winrate": "48.91%", "augments": ["信念者的强化", "咏叹奏鸣", "霸符兄弟"]},
    "27": {"name": "炼金术士 辛吉德", "tier": "T1", "winrate": "55.03%", "augments": ["潘朵拉的盒子", "舞会女王", "魄罗之王的弹跳"]},
    "28": {"name": "痛苦之拥 伊芙琳", "tier": "T4", "winrate": "48.20%", "augments": ["咏叹奏鸣", "虚空裂隙", "红包"]},
    "29": {"name": "瘟疫之源 图奇", "tier": "T3", "winrate": "50.51%", "augments": ["红包", "双刀流", "暴击飞弹"]},
    "30": {"name": "死亡颂唱者 卡尔萨斯", "tier": "T2", "winrate": "51.98%", "augments": ["祖母的辣椒油", "虚空裂隙", "咏叹奏鸣"]},
}

# Item recommendations by champion type
def get_items(name):
    # AP champions
    if any(x in name for x in ["安妮", "加里奥", "崔斯特", "费德提克", "瑞兹", "卡尔萨斯", "维迦", "辛吉德",
                                "卡萨丁", "莫甘娜", "基兰", "卡尔玛", "布兰德", "阿狸", "菲兹", "维克托",
                                "辛德拉", "索尔", "佐伊", "婕拉", "萨勒芬妮", "维克兹", "塔莉垭", "阿兹尔",
                                "妮蔻", "薇古丝", "梅尔", "彗", "莉莉娅", "乐芙兰", "弗拉基米尔", "艾尼维亚",
                                "伊芙琳", "奥莉安娜", "丽桑卓", "塞拉斯", "兰博", "卡西奥佩娅", "黑默丁格",
                                "库奇", "吉格斯", "拉克丝", "泽拉斯", "玛尔扎哈", "艾克", "提莫"]):
        return ["法穿鞋", "卢登", "影焰", "金身", "虚空", "帽子"]

    # Support champions
    if any(x in name for x in ["索拉卡", "娑娜", "迦娜", "塔里克", "璐璐", "娜美", "巴德", "洛", "米利欧",
                                "烈娜塔", "悠米"]):
        return ["CD鞋", "救赎", "香炉", "米凯尔", "帽子", "金身"]

    # Tank champions
    if any(x in name for x in ["阿利斯塔", "赛恩", "科加斯", "阿木木", "拉莫斯", "蒙多", "茂凯", "诺提勒斯",
                                "瑟庄妮", "布隆", "塔姆", "奥恩", "芮尔", "蕾欧娜", "波比", "墨菲特", "慎"]):
        return ["护甲鞋", "日炎", "荆棘", "石像", "振奋", "亡板"]

    # Default AD/Fighter
    return ["攻速鞋", "无尽", "饮血", "破败", "复活甲", "幕刃"]

# Add items to each champion
for champ_id, champ_data in champions_raw.items():
    champ_data["items"] = get_items(champ_data["name"])

# Save to file
output = {"last_update": "2026-03-17", "champions": champions_raw}
with open('champions_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Saved {len(champions_raw)} champions to champions_data.json")
