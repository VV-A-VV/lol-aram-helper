# LOL ARAM Helper - 设置指南

## 首次设置

### 方法1: 自动抓取（推荐）

**一键获取所有172个英雄数据：**

```bash
# 激活虚拟环境
source .venv/Scripts/activate  # Windows Git Bash
# 或 .venv\Scripts\activate  # Windows CMD

# 自动抓取数据
python fetch_champions.py

# 处理数据（添加装备推荐）
python auto_update.py

# 启动助手
python floating_window.py
```

### 方法2: 使用浏览器提取数据（备用）

如果自动抓取失败，可以手动提取：

**1. 提取英雄数据**
- 打开 https://hextech.dtodo.cn/zh-CN
- 点击 "显示全部" 按钮（加载所有172个英雄）
- 按 F12 打开浏览器控制台
- 复制 `extract_browser_data.js` 的内容并粘贴到控制台
- 按回车执行
- 复制输出的 JSON 数据
- 保存到 `champions_raw.json` 文件

**2. 处理数据**
```bash
python auto_update.py
```

**3. 启动助手**
```bash
python floating_window.py
```

## 日常使用

```bash
python floating_window.py
```

助手会:
- 自动连接英雄联盟客户端
- 在 ARAM 选人阶段显示推荐
- 显示: 评级、胜率、强化符文、装备

## 更新数据（每月一次）

当需要从 hextech.dtodo.cn 获取最新数据时:

1. 打开 https://hextech.dtodo.cn/zh-CN
2. 点击 "显示全部" 按钮
3. 按 F12，进入控制台
4. 粘贴 `extract_browser_data.js` 的内容
5. 复制 JSON 输出
6. 保存到 `champions_raw.json`
7. 运行 `python auto_update.py`
8. 重启助手

## 文件说明

- `champions_raw.json` - 原始数据（评级、胜率、强化符文）
- `champions_data.json` - 处理后的数据（包含装备推荐）
- `config.json` - 装备推荐配置和英雄分类
- `floating_window.py` - 主程序
- `extract_browser_data.js` - 浏览器提取脚本
- `auto_update.py` - 数据处理脚本
- `run_helper.py` - 启动器

## 自定义装备推荐

编辑 `config.json` 中的 `item_recommendations` 部分:

```json
{
  "item_recommendations": {
    "ap": ["法穿鞋", "卢登", "影焰", "金身", "虚空", "帽子"],
    "support": ["CD鞋", "救赎", "香炉", "米凯尔", "帽子", "金身"],
    "tank": ["护甲鞋", "日炎", "荆棘", "石像", "振奋", "亡板"],
    "ad": ["攻速鞋", "无尽", "饮血", "破败", "复活甲", "幕刃"]
  }
}
```

## 故障排除

**问题: 助手无法连接客户端**
- 确保英雄联盟客户端已启动
- 检查 LCU 连接器是否正常工作

**问题: 没有显示英雄推荐**
- 确保进入了 ARAM 选人阶段
- 检查 `champions_data.json` 是否包含该英雄数据

**问题: 装备推荐不准确**
- 编辑 `config.json` 中的 `champion_types` 分类
- 重新运行 `python auto_update.py`
