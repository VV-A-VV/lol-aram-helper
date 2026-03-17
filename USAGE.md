# 使用指南

## 🎯 项目简介

这是一个**自动化工具**，可以在你玩英雄联盟海克斯大乱斗时，自动检测当前可选英雄并提供 op.gg 的数据链接。

## 📋 前置要求

- Python 3.7+
- 英雄联盟客户端
- psutil 库

## 🚀 快速开始

### Windows 用户

1. 双击运行 `install.bat`
2. 启动英雄联盟客户端
3. 进入海克斯大乱斗选英雄界面
4. 运行：
   ```cmd
   cd lib
   python main.py
   ```

### macOS/Linux 用户

1. 运行安装脚本：
   ```bash
   ./install.sh
   ```
2. 启动英雄联盟客户端
3. 进入海克斯大乱斗选英雄界面
4. 运行：
   ```bash
   cd lib
   python3 main.py
   ```

## 🖥️ 图形界面模式

如果你想要一个持续监控的窗口：

```bash
python gui.py
```

这会打开一个窗口，实时显示当前选英雄状态。

## 🔧 工作原理

1. **连接客户端**：通过检测 LeagueClientUx 进程获取 API 端口和令牌
2. **获取数据**：调用 LCU API 的 `/lol-champ-select/v1/session` 端点
3. **解析英雄**：将英雄 ID 映射到名称
4. **生成链接**：创建对应的 op.gg 链接供查看

## 📊 显示信息

程序会为每个可选英雄生成 op.gg 链接，你可以在浏览器中查看：
- ⭐ Tier 等级评分
- 🔮 推荐海克斯符文
- ⚔️ 推荐装备出装
- 📈 胜率统计

## ❓ 常见问题

**Q: 提示"客户端未运行"？**
A: 确保英雄联盟客户端已启动

**Q: 提示"不在选英雄阶段"？**
A: 需要进入游戏的选英雄界面才能获取数据

**Q: 如何添加更多英雄？**
A: 编辑 `lib/main.py` 中的 `CHAMPION_ID_MAP` 字典

## 🔗 相关链接

- [op.gg 海克斯大乱斗](https://op.gg/zh-cn/lol/modes/aram-mayhem)
- [LCU API 文档](https://riot-api-libraries.readthedocs.io/en/latest/lcu.html)
