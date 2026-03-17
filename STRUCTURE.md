# 项目结构

```
lol-aram-mayhem-helper/
├── plugin.json              # Claude Code 插件配置
├── README.md                # 项目说明
├── USAGE.md                 # 使用指南
├── install.bat              # Windows 安装脚本
├── install.sh               # Linux/macOS 安装脚本
├── commands/                # 命令目录
│   └── 查询英雄.md          # 查询英雄命令
├── skills/                  # 技能目录
│   └── lol-aram-helper.md   # 助手技能
└── lib/                     # 核心代码
    ├── lcu_connector.py     # LCU API 连接器
    ├── main.py              # 主程序（命令行）
    ├── gui.py               # 图形界面
    ├── scraper.py           # 数据抓取（备用）
    └── scraper.js           # Node.js 版本（备用）
```

## 核心文件说明

### lcu_connector.py
连接英雄联盟客户端的核心模块，通过进程检测获取 API 访问权限。

### main.py
命令行主程序，自动检测当前选英雄阶段并显示信息。

### gui.py
图形界面版本，提供实时监控窗口。
