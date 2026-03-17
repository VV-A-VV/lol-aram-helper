#!/usr/bin/env node

/**
 * 英雄联盟海克斯大乱斗数据抓取工具
 * 从 op.gg 获取英雄数据
 */

const https = require('https');

// 英雄名称映射（中文到英文）
const championMap = {
  '奎因': 'quinn',
  '亚索': 'yasuo',
  '劫': 'zed',
  '阿狸': 'ahri',
  '盖伦': 'garen',
  // 可以继续添加更多英雄
};

function getChampionData(championName) {
  const englishName = championMap[championName] || championName.toLowerCase();
  const url = `https://op.gg/zh-cn/lol/modes/aram-mayhem/${englishName}/build`;

  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const parsed = parseChampionData(data, championName);
          resolve(parsed);
        } catch (error) {
          reject(error);
        }
      });
    }).on('error', reject);
  });
}

function parseChampionData(html, championName) {
  // 提取 Tier 等级
  const tierMatch = html.match(/tier["\s:]+([1-5]|S|A|B|C|D)/i);
  const tier = tierMatch ? tierMatch[1] : '未知';

  // 提取胜率
  const winRateMatch = html.match(/(\d+\.\d+)%/);
  const winRate = winRateMatch ? winRateMatch[1] + '%' : '未知';

  return {
    champion: championName,
    tier: tier,
    winRate: winRate,
    url: `https://op.gg/zh-cn/lol/modes/aram-mayhem/${championName}/build`,
    note: '详细数据请访问 op.gg 网站查看'
  };
}

// 命令行调用
if (require.main === module) {
  const championName = process.argv[2];
  if (!championName) {
    console.error('请提供英雄名称');
    process.exit(1);
  }

  getChampionData(championName)
    .then(data => console.log(JSON.stringify(data, null, 2)))
    .catch(err => console.error('错误:', err.message));
}

module.exports = { getChampionData, championMap };
