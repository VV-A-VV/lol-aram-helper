#!/usr/bin/env python3
"""
自动从 hextech.dtodo.cn 更新英雄数据
需要安装: pip install playwright
运行前: playwright install chromium
"""
import json
import asyncio
from playwright.async_api import async_playwright

async def fetch_champions_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("正在访问 hextech.dtodo.cn...")
        await page.goto('https://hextech.dtodo.cn/zh-CN')

        print("点击显示全部按钮...")
        await page.click('button:has-text("显示全部")')
        await page.wait_for_timeout(2000)

        print("提取英雄数据...")
        data = await page.evaluate('''() => {
            const rows = document.querySelectorAll('table tbody tr');
            const champions = {};
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
                        champions[id] = { name, tier, winrate, augments };
                    }
                }
            });
            return {
                last_update: new Date().toISOString().split('T')[0],
                champions: champions
            };
        }''')

        await browser.close()
        return data

def add_item_recommendations(data):
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    def get_items(name):
        for type_name, champ_list in config['champion_types'].items():
            if any(x in name for x in champ_list):
                return config['item_recommendations'][type_name]
        return config['item_recommendations']['ad']

    for champ_id, champ_data in data['champions'].items():
        champ_data['items'] = get_items(champ_data['name'])

    return data

async def main():
    print("开始更新英雄数据...")
    data = await fetch_champions_data()
    print(f"获取到 {len(data['champions'])} 个英雄")

    print("添加装备推荐...")
    data = add_item_recommendations(data)

    print("保存到 champions_data.json...")
    with open('champions_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ 更新完成！共 {len(data['champions'])} 个英雄")
    print(f"✓ 更新时间: {data['last_update']}")

if __name__ == "__main__":
    asyncio.run(main())
