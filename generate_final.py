import json

# 从浏览器提取的完整172个英雄数据
# 运行此脚本前，请先在浏览器控制台运行提取脚本，将结果保存为此变量
browser_data_json = """
请将浏览器控制台的输出粘贴到这里
"""

# 如果有 champions_raw.json 文件，从文件读取
try:
    with open('champions_raw.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"从 champions_raw.json 读取了 {len(data['champions'])} 个英雄")
except FileNotFoundError:
    print("未找到 champions_raw.json")
    print("请在浏览器控制台运行 quick_start.py 中的脚本")
    print("然后将输出保存为 champions_raw.json")
    exit(1)

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

def get_items(name):
    for type_name, champ_list in config['champion_types'].items():
        if any(x in name for x in champ_list):
            return config['item_recommendations'][type_name]
    return config['item_recommendations']['ad']

# 添加装备
for cid, cdata in data['champions'].items():
    cdata['items'] = get_items(cdata['name'])

# 保存
with open('champions_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✓ 已生成 champions_data.json，共 {len(data['champions'])} 个英雄")

# 验证贝蕾亚
if '233' in data['champions']:
    print(f"✓ 贝蕾亚数据: {data['champions']['233']['name']}")
else:
    print("✗ 未找到贝蕾亚数据")
