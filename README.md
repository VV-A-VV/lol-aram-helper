# LOL ARAM 助手

英雄联盟海克斯大乱斗模式实时助手。选人阶段显示当前英雄和可交换英雄的评级、胜率、推荐海克斯和装备；进入游戏后可以识别当前三个海克斯选项，并按当前英雄的推荐顺序标注排名。

## 功能特性

- ✅ 自动检测 LOL 客户端连接
- ✅ 实时显示选中英雄和可交换英雄
- ✅ 显示英雄评级（T1/T2/T3）和胜率
- ✅ 推荐海克斯符文和装备出装
- ✅ 对局内识别三个海克斯选项并标注排名
- ✅ 美观的悬浮窗界面
- ✅ 一键更新最新数据

## 使用方法

1. 下载 `dist/LOL_ARAM_Helper.exe`
2. 启动 LOL 客户端
3. 运行 `LOL_ARAM_Helper.exe`
4. 进入海克斯大乱斗选人界面，助手会自动显示英雄信息
5. 进入游戏后，海克斯弹出时按 `F6` 或点击"识别"，查看三个选项的推荐排名

> 对局内 overlay 需要游戏使用无边框或窗口化模式。独占全屏通常会挡住普通置顶窗口。

## 数据更新

点击程序中的"更新数据"按钮，自动从 hextech.dtodo.cn 获取最新数据。

## 技术栈

- Python 3.11
- tkinter (GUI)
- psutil (进程检测)
- rapidocr-onnxruntime / mss / keyboard / opencv-python / numpy (海克斯识别和热键)
- PyInstaller (打包)

## 开发

```bash
# 安装依赖
uv pip install -r requirements.txt

# 运行程序
uv run python floating_window.py

# 运行测试
uv run python -m unittest discover -s tests -p "test_*.py" -v

# 打包
uv run python build.py
```

## 许可

MIT License
