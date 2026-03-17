#!/usr/bin/env python3
"""
英雄联盟海克斯大乱斗自动助手
自动检测当前可选英雄并显示推荐信息
"""

import json
import sys
from lcu_connector import LCUConnector

# 英雄 ID 到名称映射（部分示例）
CHAMPION_ID_MAP = {
    1: 'Annie', 2: 'Olaf', 3: 'Galio', 4: 'TwistedFate', 5: 'XinZhao',
    6: 'Urgot', 7: 'LeBlanc', 8: 'Vladimir', 9: 'Fiddlesticks', 10: 'Kayle',
    11: 'MasterYi', 12: 'Alistar', 13: 'Ryze', 14: 'Sion', 15: 'Sivir',
    16: 'Soraka', 17: 'Teemo', 18: 'Tristana', 19: 'Warwick', 20: 'Nunu',
    21: 'MissFortune', 22: 'Ashe', 23: 'Tryndamere', 24: 'Jax', 25: 'Morgana',
    26: 'Zilean', 27: 'Singed', 28: 'Evelynn', 29: 'Twitch', 30: 'Karthus',
    31: 'Chogath', 32: 'Amumu', 33: 'Rammus', 34: 'Anivia', 35: 'Shaco',
    36: 'DrMundo', 37: 'Sona', 38: 'Kassadin', 39: 'Irelia', 40: 'Janna',
    41: 'Gangplank', 42: 'Corki', 43: 'Karma', 44: 'Taric', 45: 'Veigar',
    50: 'Swain', 51: 'Caitlyn', 53: 'Blitzcrank', 54: 'Malphite', 55: 'Katarina',
    56: 'Nocturne', 57: 'Maokai', 58: 'Renekton', 59: 'JarvanIV', 60: 'Elise',
    61: 'Orianna', 62: 'Wukong', 63: 'Brand', 64: 'LeeSin', 67: 'Vayne',
    68: 'Rumble', 69: 'Cassiopeia', 72: 'Skarner', 74: 'Heimerdinger', 75: 'Nasus',
    76: 'Nidalee', 77: 'Udyr', 78: 'Poppy', 79: 'Gragas', 80: 'Pantheon',
    81: 'Ezreal', 82: 'Mordekaiser', 83: 'Yorick', 84: 'Akali', 85: 'Kennen',
    86: 'Garen', 89: 'Leona', 90: 'Malzahar', 91: 'Talon', 92: 'Riven',
    96: 'KogMaw', 98: 'Shen', 99: 'Lux', 101: 'Xerath', 102: 'Shyvana',
    103: 'Ahri', 104: 'Graves', 105: 'Fizz', 106: 'Volibear', 107: 'Rengar',
    110: 'Varus', 111: 'Nautilus', 112: 'Viktor', 113: 'Sejuani', 114: 'Fiora',
    115: 'Ziggs', 117: 'Lulu', 119: 'Draven', 120: 'Hecarim', 121: 'Khazix',
    122: 'Darius', 126: 'Jayce', 127: 'Lissandra', 131: 'Diana', 133: 'Quinn',
    134: 'Syndra', 136: 'AurelionSol', 141: 'Kayn', 142: 'Zoe', 143: 'Zyra',
    145: 'Kaisa', 147: 'Seraphine', 150: 'Gnar', 154: 'Zac', 157: 'Yasuo',
    161: 'Velkoz', 163: 'Taliyah', 164: 'Camille', 166: 'Akshan', 200: 'Belveth',
    201: 'Braum', 202: 'Jhin', 203: 'Kindred', 221: 'Zeri', 222: 'Jinx',
    223: 'TahmKench', 234: 'Viego', 235: 'Senna', 236: 'Lucian', 238: 'Zed',
    240: 'Kled', 245: 'Ekko', 246: 'Qiyana', 254: 'Vi', 266: 'Aatrox',
    267: 'Nami', 268: 'Azir', 350: 'Yuumi', 360: 'Samira', 412: 'Thresh',
    420: 'Illaoi', 421: 'RekSai', 427: 'Ivern', 429: 'Kalista', 432: 'Bard',
    497: 'Rakan', 498: 'Xayah', 516: 'Ornn', 517: 'Sylas', 518: 'Neeko',
    523: 'Aphelios', 526: 'Rell', 555: 'Pyke', 711: 'Vex', 777: 'Yone',
    875: 'Sett', 876: 'Lillia', 887: 'Gwen', 888: 'Renata', 895: 'Nilah',
    897: 'KSante', 902: 'Milio', 910: 'Hwei', 950: 'Naafiri'
}

def get_opgg_url(champion_name):
    """生成 op.gg URL"""
    return f'https://op.gg/zh-cn/lol/modes/aram-mayhem/{champion_name.lower()}/build'

def main():
    print("🎮 正在连接英雄联盟客户端...")

    connector = LCUConnector()
    if not connector.base_url:
        print("❌ 错误：未检测到运行中的英雄联盟客户端")
        print("请先启动游戏客户端")
        sys.exit(1)

    print("✅ 已连接到客户端")
    print("\n🔍 正在获取选英雄数据...")

    session = connector.get_champ_select_session()

    if 'error' in session or 'httpStatus' in session:
        print("⚠️  当前不在选英雄阶段")
        print("请进入海克斯大乱斗选英雄界面后重试")
        sys.exit(0)

    print("\n📋 当前可选英雄信息：\n")
    print("=" * 60)

    # 获取可选英雄
    pickable = session.get('myTeam', [{}])[0].get('championId', 0)

    if pickable == 0:
        print("暂无可选英雄数据")
    else:
        champ_name = CHAMPION_ID_MAP.get(pickable, f"Unknown_{pickable}")
        url = get_opgg_url(champ_name)

        print(f"英雄: {champ_name}")
        print(f"查看详情: {url}")
        print(f"\n💡 在浏览器中打开上述链接查看：")
        print(f"   - Tier 等级")
        print(f"   - 推荐海克斯符文")
        print(f"   - 推荐装备")

    print("=" * 60)

if __name__ == '__main__':
    main()
