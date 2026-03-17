// 浏览器控制台脚本 - 从 hextech.dtodo.cn 提取英雄数据
// 使用方法:
// 1. 打开 https://hextech.dtodo.cn/zh-CN
// 2. 点击 "显示全部" 按钮加载所有英雄
// 3. 按 F12 打开控制台
// 4. 粘贴此脚本并回车
// 5. 复制输出的 JSON 数据
// 6. 保存到 champions_raw.json

(function() {
    const rows = document.querySelectorAll('table tbody tr');
    const champions = {};

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
            const link = cells[1].querySelector('a');
            const id = link?.href.match(/champion-stats\/(\d+)/)?.[1];
            if (id) {
                const name = cells[1].textContent.trim().split('\n')[0].replace(/攻略$/, '').trim();
                const tier = cells[2].textContent.trim();
                const winrate = cells[3].textContent.trim();
                const augmentLinks = cells[5].querySelectorAll('a');
                const augments = Array.from(augmentLinks).slice(0, 3).map(a =>
                    a.querySelector('img')?.alt || a.textContent.trim()
                );
                champions[id] = { name, tier, winrate, augments };
            }
        }
    });

    const output = {
        last_update: new Date().toISOString().split('T')[0],
        champions: champions
    };

    console.log(JSON.stringify(output, null, 2));
    console.log(`\n✓ 提取了 ${Object.keys(champions).length} 个英雄`);
    console.log('请复制上面的 JSON 数据并保存到 champions_raw.json');
})();
