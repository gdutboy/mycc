---
name: wechatbot
layer: 基础层
authorization: B区（执行后通知）
output_levels: L1
platform: windows
---

# Desktop — CC 桌面操控 (Windows)

## 前置安装

```bash
pip install pyautogui mss Pillow easyocr numpy
```

## 核心功能

### 1. 鼠标/键盘控制

```powershell
# 移动鼠标
powershell -File control.ps1 mouse:move:500:300

# 点击
powershell -File control.ps1 mouse:click:500:300

# 输入文字
powershell -File control.ps1 type:"Hello"

# 快捷键
powershell -File control.ps1 shortcut:c:Ctrl
```

### 2. OCR 识别

```powershell
# 鼠标附近 OCR
python ocr-easy.py --cursor

# 全屏 OCR
python ocr-easy.py --screen
```

### 3. 微信 AI 机器人

启动：
```powershell
python wechatbot.py
```

触发词：`@MYCC`（大小写不敏感）

## 文件说明

| 文件 | 用途 |
|------|------|
| control.ps1 | 鼠标键盘控制 |
| ocr-easy.py | EasyOCR 识别 |
| wechatbot.py | AI 机器人 |
| wechat-read.ps1 | 微信读取 |
| wechat-send.ps1 | 微信发送 |
| .env | 配置文件 |
