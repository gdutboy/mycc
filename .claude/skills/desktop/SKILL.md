---
name: desktop
description: Use when 用户明确要在 Windows 桌面上执行可见操作时触发，如截图、点击、输入、切换窗口、读取界面信息；不用于纯代码分析、非桌面任务或只解释自动化能力的场景
layer: 基础层
authorization: B区（执行后通知）
output_levels: L1
status: ready
platform: Windows
---

# Desktop Skill — 执行流程

## 变量约定

```bash
DESKTOP=".claude/skills/desktop/desktop.py"
SKILL_DIR=".claude/skills/desktop"
```

## 核心命令

```bash
# 感知
python $DESKTOP --screenshot screen.png --ocr   # 截图 + OCR
python $DESKTOP --cursor                         # 鼠标附近 OCR
python $DESKTOP --find "文字"                    # 查找文字坐标
python $DESKTOP --windows                        # 列出所有窗口

# 操控
python $DESKTOP --click X Y
python $DESKTOP --double-click X Y
python $DESKTOP --right-click X Y
python $DESKTOP --move X Y
python $DESKTOP --type "文字"                    # 中文自动剪贴板
python $DESKTOP --press enter
python $DESKTOP --hotkey ctrl c
python $DESKTOP --activate "窗口名"
```

## 标准执行流程

1. **截图感知** → `--screenshot --ocr` 获取当前屏幕内容
2. **定位目标** → `--find "文字"` 或从 OCR 结果提取坐标
3. **执行操作** → click / type / hotkey
4. **验证结果** → `--cursor` 或再次截图确认

## 安全规则

| 级别 | 操作 | 策略 |
|------|------|------|
| 绿色 | 截图、OCR、读窗口、移动鼠标 | 自动执行 |
| 黄色 | 点击、输入文字、切换窗口 | 执行并告知用户 |
| 红色 | 涉及密码、支付、删除、发消息 | 先问用户 |

禁止操控系统关键窗口、输入密码、操作支付页面。

## 微信专用脚本

```bash
python $SKILL_DIR/wechat-read.py          # 读取聊天内容
python $SKILL_DIR/wechat-send.py "消息"   # 发送消息（自动验证）
python $SKILL_DIR/wechat-send-file.py /path/to/file
python $SKILL_DIR/wechat-monitor.py       # 后台监控 @MYCC
```

## 依赖安装

```bash
pip install pyautogui Pillow pygetwindow mss winocr
```

OCR 使用 Windows 10+ 内置引擎，无需额外安装。

详细参考：同目录下 REFERENCE.md
