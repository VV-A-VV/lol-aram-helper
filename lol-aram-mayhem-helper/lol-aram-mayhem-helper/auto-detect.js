const { getLCUInfo, lcuRequest } = require('./lcu-client');

const CHAMPIONS = {
  1: '安妮', 2: '奥拉夫', 3: '加里奥', 4: '崔斯特', 5: '赵信',
  11: '易', 17: '提莫', 18: '崔丝塔娜', 22: '艾希', 23: '蛮王',
  51: '凯特琳', 67: '薇恩', 81: '伊泽瑞尔', 86: '盖伦', 103: '阿狸',
  157: '亚索', 222: '金克斯', 238: '劫', 777: '永恩'
};

async function main() {
  console.log('🎮 LOL 海克斯大乱斗助手');
  console.log('正在连接客户端...\n');

  const info = getLCUInfo();
  if (!info) {
    console.log('❌ 未检测到LOL客户端运行');
    console.log('请先启动游戏客户端');
    return;
  }

  console.log('✅ 已连接客户端');
  console.log('监听选英雄阶段...\n');

  setInterval(async () => {
    try {
      const session = await lcuRequest(info, '/lol-champ-select/v1/session');

      if (session.myTeam) {
        console.clear();
        console.log('🎮 当前可选英雄：\n');
        console.log('='.repeat(50));

        const pickable = session.myTeam[0]?.championId || 0;
        if (pickable) {
          const name = CHAMPIONS[pickable] || `ID:${pickable}`;
          const url = `https://op.gg/zh-cn/lol/modes/aram-mayhem`;
          console.log(`\n英雄: ${name}`);
          console.log(`查看: ${url}\n`);
        }
        console.log('='.repeat(50));
      }
    } catch (e) {}
  }, 2000);
}

main();
