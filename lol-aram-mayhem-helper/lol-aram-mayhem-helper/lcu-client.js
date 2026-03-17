const https = require('https');
const { execSync } = require('child_process');

// 获取LOL客户端信息
function getLCUInfo() {
  try {
    const cmd = process.platform === 'win32'
      ? 'wmic PROCESS WHERE name="LeagueClientUx.exe" GET commandline'
      : 'ps aux | grep LeagueClientUx';

    const output = execSync(cmd, { encoding: 'utf8' });
    const portMatch = output.match(/--app-port=(\d+)/);
    const tokenMatch = output.match(/--remoting-auth-token=([\w-]+)/);

    if (portMatch && tokenMatch) {
      return { port: portMatch[1], token: tokenMatch[1] };
    }
  } catch (e) {}
  return null;
}

// 调用LCU API
function lcuRequest(info, path) {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(`riot:${info.token}`).toString('base64');
    const options = {
      hostname: '127.0.0.1',
      port: info.port,
      path: path,
      method: 'GET',
      headers: { 'Authorization': `Basic ${auth}` },
      rejectUnauthorized: false
    };

    https.get(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

module.exports = { getLCUInfo, lcuRequest };
