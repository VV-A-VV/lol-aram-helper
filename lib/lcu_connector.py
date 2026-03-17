#!/usr/bin/env python3
"""
LOL 客户端连接器 - 自动获取游戏数据
通过 LCU API 连接到英雄联盟客户端
"""

import json
import base64
import urllib.request
import urllib.error
import ssl
import psutil
import re

class LCUConnector:
    def __init__(self):
        self.port = None
        self.token = None
        self.base_url = None
        self._connect()

    def _connect(self):
        """连接到 LOL 客户端"""
        for proc in psutil.process_iter(['name', 'cmdline']):
            if proc.info['name'] in ['LeagueClientUx.exe', 'LeagueClientUx']:
                cmdline = ' '.join(proc.info['cmdline'])

                port_match = re.search(r'--app-port=(\d+)', cmdline)
                token_match = re.search(r'--remoting-auth-token=([\w-]+)', cmdline)

                if port_match and token_match:
                    self.port = port_match.group(1)
                    self.token = token_match.group(1)
                    self.base_url = f'https://127.0.0.1:{self.port}'
                    return True
        return False

    def request(self, endpoint):
        """发送 API 请求"""
        if not self.base_url:
            return {'error': 'LOL 客户端未运行'}

        url = f'{self.base_url}{endpoint}'
        auth = base64.b64encode(f'riot:{self.token}'.encode()).decode()

        req = urllib.request.Request(url, headers={'Authorization': f'Basic {auth}'})

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                return json.loads(response.read().decode())
        except urllib.error.URLError as e:
            return {'error': str(e)}

    def get_champ_select_session(self):
        """获取当前选英雄会话"""
        return self.request('/lol-champ-select/v1/session')

    def get_available_champions(self):
        """获取可选英雄列表"""
        session = self.get_champ_select_session()
        if 'error' in session:
            return session

        if 'myTeam' in session:
            pickable_ids = session.get('actions', [[]])[0]
            return [action.get('championId') for action in pickable_ids if action.get('type') == 'pick']

        return []

if __name__ == '__main__':
    connector = LCUConnector()
    champions = connector.get_available_champions()
    print(json.dumps(champions, ensure_ascii=False, indent=2))
