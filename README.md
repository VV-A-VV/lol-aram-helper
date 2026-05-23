# LOL ARAM Mayhem Helper

英雄联盟海克斯大乱斗实时助手。选人阶段显示当前英雄与可交换英雄的 T 级、胜率、推荐海克斯和装备参考；进入游戏后，按 `F6` 识别当前三个海克斯选项，并按当前英雄的适配排名标注选择优先级。

## 功能

- 自动连接本机 LOL 客户端 LCU
- 选人阶段显示当前英雄和可交换英雄信息
- 对局中支持全局热键 `F6` 触发 OCR 识别
- 识别三个海克斯选项，并显示该英雄下的总排名
- 按总排名五分位标色，方便判断是否刷新
- 程序内一键更新最新英雄和海克斯数据
- PyInstaller 单文件打包，产物在 `dist/LOL_ARAM_Helper.exe`

## 排名颜色

OCR 结果会显示类似 `总排 #3/60 · 前20%`：

- 金色：前 20%
- 绿色：前 40%
- 蓝色：前 60%
- 橙色：前 80%
- 红色：后 20% 或未收录

排名基于每个英雄详情页的完整海克斯推荐列表，不再只使用首页前三个预览推荐。

## 使用方法

1. 启动 LOL 客户端。
2. 运行 [dist/LOL_ARAM_Helper.exe](dist/LOL_ARAM_Helper.exe)。
3. 进入海克斯大乱斗选人界面，助手会自动显示英雄信息。
4. 进入游戏后，海克斯选择界面弹出时按 `F6`。
5. 查看浮窗或屏幕中上方 overlay 的三个选项排名。

对局内 overlay 需要游戏使用无边框或窗口化模式。独占全屏通常会盖住普通置顶窗口。如果 `F6` 没反应，优先尝试用管理员权限运行助手。

## 数据说明

数据更新来自 `https://hextech.dtodo.cn/zh-CN`：

- 首页用于获取英雄列表、T 级、胜率和详情页入口。
- 海克斯总表用于建立海克斯 ID 到中文名的映射。
- 每个英雄详情页用于获取完整海克斯适配排名。

当前版本会为每个英雄保存 60+ 个海克斯推荐项，OCR 排名和五分位都基于这个完整列表。装备仍是内置参考数据，主要决策请以海克斯排名为准。

## 开发

```bash
# 安装依赖
uv pip install -r requirements.txt

# 运行程序
uv run python floating_window.py

# 运行测试
uv run python -m unittest discover -s tests -p "test_*.py" -v

# 打包 Windows exe
uv run python build.py
```

## 项目结构

- `floating_window.py`：程序入口
- `aram_helper/ui.py`：Tkinter 界面和 overlay
- `aram_helper/app_state.py`：游戏阶段和当前英雄检测
- `aram_helper/lcu_client.py`：LCU API 客户端
- `aram_helper/ocr_service.py`：截图和 OCR 识别
- `aram_helper/recommendations.py`：海克斯匹配、排名和五分位
- `aram_helper/data_update.py`：英雄与海克斯数据更新
- `champions_data.json`：离线数据文件

## 打包产物

当前可执行文件：

```text
dist/LOL_ARAM_Helper.exe
```

打包时会把 `champions_data.json` 一起嵌入。首次运行打包版时，如果当前目录没有数据文件，程序会释放一份本地 `champions_data.json`，之后可通过界面按钮更新。

## 许可

MIT License
