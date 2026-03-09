---
name: desktop
description: 桌面操控。让 CC 看屏幕、动鼠标、点按钮、输文字。支持 Windows 系统。触发词："/desktop"、"帮我操作桌面"、"点一下那个按钮"、"看看屏幕上有什么"
layer: 基础层
authorization: B区（执行后通知）
output_levels: L1
status: ready
platform: Windows
---

# Desktop — CC 桌面操控 (Windows 版)

## 快速开始

```bash
# 脚本路径
DESKTOP=".claude/skills/desktop/desktop.py"

# ===== 眼（感知） =====

# 截图
python $DESKTOP --screenshot output.png

# 全屏 OCR 识别文字
python $DESKTOP --screenshot --ocr

# 鼠标附近 OCR（触觉模式）
python $DESKTOP --cursor

# 获取鼠标位置
python $DESKTOP --cursor-pos

# 列出所有窗口
python $DESKTOP --windows

# 查找文字位置
python $DESKTOP --find "按钮文字"

# ===== 手（操控） =====

# 移动鼠标
python $DESKTOP --move 500 300

# 点击
python $DESKTOP --click 500 300

# 双击
python $DESKTOP --double-click 500 300

# 右键点击
python $DESKTOP --right-click 500 300

# 输入文字
python $DESKTOP --type "Hello World"

# 按键
python $DESKTOP --press enter
python $DESKTOP --press tab
python $DESKTOP --press escape

# 组合键
python $DESKTOP --hotkey ctrl c   # 复制
python $DESKTOP --hotkey ctrl v   # 粘贴
python $DESKTOP --hotkey alt f4   # 关闭窗口

# ===== 窗口管理 =====

# 激活窗口（模糊匹配）
python $DESKTOP --activate "微信"

# 获取活动窗口
python $DESKTOP --active-window
```

## 安装依赖

```bash
pip install pyautogui Pillow pygetwindow mss winocr
```

**说明**：`winocr` 调用 Windows 10+ 内置 OCR 引擎，无需额外安装任何 OCR 软件。

## 常用命令速查

| 功能 | 命令 |
|------|------|
| 鼠标位置 | `--cursor-pos` |
| 截图 | `--screenshot file.png` |
| OCR 文字 | `--screenshot --ocr` |
| 鼠标附近 OCR | `--cursor` |
| 移动鼠标 | `--move X Y` |
| 点击 | `--click X Y` |
| 输入文字 | `--type TEXT` |
| 按键 | `--press enter` |
| 组合键 | `--hotkey ctrl c` |
| 关闭窗口 | `--hotkey alt f4` |
| 列出窗口 | `--windows` |
| 激活窗口 | `--activate 窗口名` |
| 查找文字 | `--find TEXT` |

## 操作流程

### 标准流程：点击按钮

```
1. 截图找目标
   python $DESKTOP --screenshot screen.png --ocr
   → 找到 "保存按钮" @ (550, 300)

2. 点击
   python $DESKTOP --click 550 300

3. 验证结果
   python $DESKTOP --cursor
```

### 文字输入

```
1. 点击输入框
   python $DESKTOP --click 400 200

2. 输入文字
   python $DESKTOP --type "要输入的内容"

3. 确认提交
   python $DESKTOP --press enter
```

### 查找并点击

```
1. 查找文字位置
   python $DESKTOP --find "提交"
   → 返回 {"found": true, "center": [550, 300]}

2. 点击
   python $DESKTOP --click 550 300
```

## 安全规则

| 级别 | 操作 | 策略 |
|------|------|------|
| 绿色 | 截图、OCR、读窗口、移动鼠标 | 自动执行 |
| 黄色 | 点击、输入文字、切换窗口 | 执行并告知用户 |
| 红色 | 涉及密码、支付、删除，发消息 | 先问用户 |

**禁区**：
- 不操控系统关键窗口
- 不输入密码
- 不操作支付页面
- 不修改系统设置

## 性能参考

| 操作 | 耗时 |
|------|------|
| 鼠标移动/点击 | < 10ms |
| 截图 | ~100ms |
| 全屏 OCR (winocr) | 0.5-1.5s |
| 局部 OCR (winocr) | 0.2-0.5s |
| 窗口列表 | < 100ms |

## 微信操控脚本

本 skill 目录下有专用的微信操控脚本，封装了完整的读/发/验证/监控流程：

```bash
SKILL_DIR=".claude/skills/desktop"

# 读取当前聊天内容
python $SKILL_DIR/wechat-read.py              # 简洁文字
python $SKILL_DIR/wechat-read.py --bbox       # JSON 包围盒

# 发送文字消息（自动验证）
python $SKILL_DIR/wechat-send.py "消息内容"

# 发送文件/图片
python $SKILL_DIR/wechat-send-file.py /path/to/file

# 后台监控（检测 @MYCC 触发）
python $SKILL_DIR/wechat-monitor.py           # 默认关键词 MYCC
python $SKILL_DIR/wechat-monitor.py "自定义关键词"
```

### 使用前提
- 微信已打开并停留在目标聊天窗口
- 已安装 Python 依赖：`pip install pyautogui Pillow pygetwindow mss winocr`

### 关键参数（可通过环境变量覆盖）
- `WECHAT_SIDEBAR=320`：微信侧边栏宽度（图标+联系人列表）
- `WECHAT_TITLE_H=60`：顶部标题栏高度
- `WECHAT_INPUT_H=160`：底部输入框+工具栏高度

### 注意事项
- **中文输入**：通过剪贴板粘贴（`--type` 也已改用剪贴板方式）
- **坐标动态获取**：每次操作前自动获取窗口位置，不硬编码
- **OCR 验证**：发送后 OCR 输入框，count==0 = 发送成功

## OCR 说明

使用 Windows 10+ 内置 OCR 引擎（通过 `winocr` 调用），支持中英文识别，无需额外安装任何 OCR 软件。

---

*Windows 版 Desktop Skill - 2026-03-09*
