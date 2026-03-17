# LOL ARAM 助手

英雄联盟大乱斗模式实时助手，在选人阶段显示英雄评级、胜率、符文和装备推荐。

## 功能特性

- ✅ 自动检测 LOL 客户端连接
- ✅ 实时显示选中英雄和可交换英雄
- ✅ 显示英雄评级（T1/T2/T3）和胜率
- ✅ 推荐海克斯符文和装备出装
- ✅ 美观的悬浮窗界面
- ✅ 一键更新最新数据

## 使用方法

1. 下载 `dist/LOL_ARAM_Helper.exe`
2. 启动 LOL 客户端
3. 运行 `LOL_ARAM_Helper.exe`
4. 进入 ARAM 选人界面，助手会自动显示英雄信息

## 数据更新

点击程序中的"更新数据"按钮，自动从 hextech.dtodo.cn 获取最新数据。

## 技术栈

- Python 3.11
- tkinter (GUI)
- psutil (进程检测)
- PyInstaller (打包)

## 开发

```bash
# 安装依赖
uv pip install -r requirements.txt

# 运行程序
uv run python floating_window.py

# 打包
uv run pyinstaller --name=LOL_ARAM_Helper --onefile --windowed --add-data="champions_data.json;." --hidden-import=psutil --clean floating_window.py
```

## 许可

MIT License
