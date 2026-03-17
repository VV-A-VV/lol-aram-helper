import json

# Read the raw data from browser extraction
raw_data = {
  "last_update": "2026-03-17",
  "champions": {}
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
                                "烈娜塔", "悠米", "卡尔玛"]):
        return ["CD鞋", "救赎", "香炉", "米凯尔", "帽子", "金身"]

    # Tank champions
    if any(x in name for x in ["阿利斯塔", "赛恩", "科加斯", "阿木木", "拉莫斯", "蒙多", "茂凯", "诺提勒斯",
                                "瑟庄妮", "布隆", "塔姆", "奥恩", "芮尔", "蕾欧娜", "波比", "墨菲特", "慎"]):
        return ["护甲鞋", "日炎", "荆棘", "石像", "振奋", "亡板"]

    # Default AD/Fighter
    return ["攻速鞋", "无尽", "饮血", "破败", "复活甲", "幕刃"]

# This will be filled with data
champions_list = []

print("Script ready. Run with champion data.")
