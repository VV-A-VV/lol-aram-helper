# 🎮 英雄联盟海克斯大乱斗助手

## ✅ 已完成功能

### 核心特性
✔️ **自动检测游戏状态** - 通过 LCU API 连接客户端
✔️ **实时获取可选英雄** - 无需手动输入
✔️ **生成 op.gg 链接** - 快速查看 Tier/符文/装备
✔️ **命令行 + GUI 双模式** - 灵活使用
✔️ **跨平台支持** - Windows/macOS/Linux

## 🎯 使用场景

1. 启动 LOL 客户端
2. 进入海克斯大乱斗选英雄界面
3. 运行程序：`python lib/main.py`
4. 自动显示当前可选英雄的 op.gg 链接

## 📦 文件清单

- `lib/lcu_connector.py` - 客户端连接器（核心）
- `lib/main.py` - 命令行主程序
- `lib/gui.py` - 图形界面版本
- `install.bat/sh` - 一键安装脚本

## 🚀 快速开始

```bash
# 安装依赖
pip install psutil

# 运行
python lib/main.py
```

## 💡 技术亮点

- 使用 LCU API 实现游戏数据自动获取
- 进程检测自动获取认证信息
- 支持 160+ 英雄 ID 映射
- 实时监控选英雄状态

---

**数据来源**: [op.gg](https://op.gg/zh-cn/lol/modes/aram-mayhem)
