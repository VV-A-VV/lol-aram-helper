import json
import subprocess
import sys

def update_champion_data():
    """使用Playwright从hextech.dtodo.cn获取最新英雄数据"""

    print("正在从 hextech.dtodo.cn 获取最新数据...")

    # 使用Playwright获取数据
    js_code = '''
    const rows = document.querySelectorAll('table tbody tr');
    const data = {};
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
            const link = cells[1].querySelector('a');
            const id = link ? link.href.match(/champion-stats\\/(\\d+)/)?.[1] : null;
            if (id) {
                const name = cells[1].textContent.trim().split('\\n')[0].replace(/攻略$/, '').trim();
                const tier = cells[2].textContent.trim();
                const winrate = cells[3].textContent.trim();
                const augmentLinks = cells[5].querySelectorAll('a');
                const augments = Array.from(augmentLinks).slice(0, 3).map(a => {
                    const img = a.querySelector('img');
                    return img ? img.alt : a.textContent.trim();
                });
                data[id] = { name, tier, winrate, augments };
            }
        }
    });
    return JSON.stringify({last_update: new Date().toISOString().split('T')[0], champions: data});
    '''

    # 调用Playwright
    cmd = [
        'uvx', '--from', 'playwright', 'playwright', 'codegen',
        '--target', 'javascript',
        'https://hextech.dtodo.cn/zh-CN'
    ]

    print("提示：需要手动运行Playwright获取数据")
    print("或者使用已有的champions_data.json")

    return None

def get_items(name):
    """根据英雄类型返回推荐装备"""
    # AP英雄
    if any(x in name for x in ["安妮", "加里奥", "崔斯特", "费德提克", "瑞兹", "卡尔萨斯", "维迦", "辛吉德",
                                "卡萨丁", "莫甘娜", "基兰", "卡尔玛", "布兰德", "阿狸", "菲兹", "维克托",
                                "辛德拉", "索尔", "佐伊", "婕拉", "萨勒芬妮", "维克兹", "塔莉垭", "阿兹尔",
                                "妮蔻", "薇古丝", "梅尔", "彗", "莉莉娅", "乐芙兰", "弗拉基米尔", "艾尼维亚",
                                "伊芙琳", "奥莉安娜", "丽桑卓", "塞拉斯", "兰博", "卡西奥佩娅", "黑默丁格",
                                "库奇", "吉格斯", "拉克丝", "泽拉斯", "玛尔扎哈", "艾克", "提莫"]):
        return ["法穿鞋", "卢登", "影焰", "金身", "虚空", "帽子"]

    # 辅助英雄
    if any(x in name for x in ["索拉卡", "娑娜", "迦娜", "塔里克", "璐璐", "娜美", "巴德", "洛", "米利欧",
                                "烈娜塔", "悠米"]):
        return ["CD鞋", "救赎", "香炉", "米凯尔", "帽子", "金身"]

    # 坦克英雄
    if any(x in name for x in ["阿利斯塔", "赛恩", "科加斯", "阿木木", "拉莫斯", "蒙多", "茂凯", "诺提勒斯",
                                "瑟庄妮", "布隆", "塔姆", "奥恩", "芮尔", "蕾欧娜", "波比", "墨菲特", "慎"]):
        return ["护甲鞋", "日炎", "荆棘", "石像", "振奋", "亡板"]

    # 默认AD/战士
    return ["攻速鞋", "无尽", "饮血", "破败", "复活甲", "幕刃"]

def process_data(raw_data):
    """处理原始数据，添加装备推荐"""
    for champ_id, champ_data in raw_data["champions"].items():
        champ_data["items"] = get_items(champ_data["name"])
    return raw_data

if __name__ == "__main__":
    # 从现有文件读取或更新
    try:
        with open('champions_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"当前数据: {len(data['champions'])} 个英雄")
            print(f"更新日期: {data['last_update']}")
    except FileNotFoundError:
        print("未找到champions_data.json，需要首次获取数据")
        sys.exit(1)
