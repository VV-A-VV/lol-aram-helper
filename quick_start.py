#!/usr/bin/env python3
"""
一键生成完整数据文件
从浏览器控制台复制JSON数据后运行此脚本
"""
import json

# 步骤1: 在浏览器控制台运行以下代码获取数据
print("=" * 60)
print("步骤1: 打开 https://hextech.dtodo.cn/zh-CN")
print("步骤2: 点击'显示全部 172 条'按钮")
print("步骤3: 在浏览器控制台(F12)运行以下代码:")
print("=" * 60)
print("""
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
copy(JSON.stringify({last_update: new Date().toISOString().split('T')[0], champions: champions}, null, 2));
console.log('已复制到剪贴板！共', Object.keys(champions).length, '个英雄');
""")
print("=" * 60)
print("步骤4: 数据已自动复制到剪贴板")
print("步骤5: 将数据粘贴保存为 champions_raw.json")
print("步骤6: 运行 python auto_update.py 添加装备推荐")
print("=" * 60)
