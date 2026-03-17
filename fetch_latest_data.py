#!/usr/bin/env python3
"""
自动从hextech.dtodo.cn更新英雄数据
使用方法: python fetch_latest_data.py
"""
import json
import subprocess
import sys
from datetime import datetime

def load_config():
    """加载配置文件"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_items(name, config):
    """根据英雄类型返回推荐装备"""
    for type_name, champions in config['champion_types'].items():
        if any(x in name for x in champions):
            return config['item_recommendations'][type_name]
    return config['item_recommendations']['ad']

def fetch_data_with_playwright():
    """使用Playwright获取数据"""
    print("正在启动浏览器获取数据...")

    # JavaScript代码用于提取数据
    js_code = """
    async () => {
        // 点击显示全部按钮
        const showAllBtn = document.querySelector('button:has-text("显示全部")');
        if (showAllBtn) {
            showAllBtn.click();
            await new Promise(r => setTimeout(r, 1000));
        }

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
        return JSON.stringify(data);
    }
    """

    print("提示：需要手动使用Playwright获取数据")
    print("请运行以下命令：")
    print("uvx playwright codegen https://hextech.dtodo.cn/zh-CN")
    return None

def save_data(data, config):
    """保存数据到文件"""
    output_file = config['output_file']
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ 数据已保存到 {output_file}")
    print(f"✓ 共 {len(data['champions'])} 个英雄")

if __name__ == "__main__":
    config = load_config()
    print(f"数据源: {config['data_source']}")
    print("=" * 50)

    # 由于Playwright需要交互，这里提供说明
    print("\n自动更新步骤：")
    print("1. 确保已安装Playwright: uvx playwright install")
    print("2. 运行浏览器脚本获取数据")
    print("3. 数据会自动添加装备推荐并保存\n")
