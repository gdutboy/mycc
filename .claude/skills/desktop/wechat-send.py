#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
wechat-send.py — 发送微信消息并自动验证（Windows 版）
用法: python wechat-send.py "消息内容"
输出: 验证结果
"""
import sys
import os
import io
import json
import time
import subprocess
import asyncio

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pyautogui
import pygetwindow as gw
from PIL import ImageEnhance
from core.runtime import build_executor

try:
    import winocr
except ImportError:
    print("[error] winocr 未安装，请运行: pip install winocr", file=sys.stderr)
    sys.exit(1)

# 微信 Windows 版 UI 参数
SIDEBAR = int(os.environ.get("WECHAT_SIDEBAR", 320))
INPUT_H = int(os.environ.get("WECHAT_INPUT_H", 160))


def find_wechat_window():
    for w in gw.getAllWindows():
        if w.title == "微信" and w.width > 400:
            return w
    return None


def copy_to_clipboard(text):
    """通过临时文件 + PowerShell 写入剪贴板（支持中文）"""
    import tempfile
    # 写入临时文件（UTF-8 with BOM，PowerShell 能正确读取）
    tmp = os.path.join(tempfile.gettempdir(), "wechat_clip.txt")
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    subprocess.run(
        ['powershell', '-command',
         f'Get-Content -Path "{tmp}" -Encoding UTF8 -Raw | Set-Clipboard'],
        capture_output=True
    )


async def send_message(message):
    win = find_wechat_window()
    if not win:
        print("[error] 微信窗口未找到", file=sys.stderr)
        sys.exit(1)

    executor = build_executor()

    # 1. 激活微信
    try:
        win.activate()
        time.sleep(0.5)
    except Exception:
        pass

    # 2. 复制消息到剪贴板
    copy_to_clipboard(message)
    time.sleep(0.1)

    # 3. 点击输入框（聊天区域底部中央）
    input_x = win.left + SIDEBAR + (win.width - SIDEBAR) // 2
    input_y = win.top + win.height - 50
    executor.click(input_x, input_y)
    time.sleep(0.2)

    # 4. 粘贴
    executor.hotkey('ctrl', 'v')
    time.sleep(0.3)

    # 5. 回车发送
    executor.press('enter')

    # 6. 等待后验证
    time.sleep(1.0)

    # OCR 验证输入框是否清空
    # 只截输入框文本区，排除底部按钮栏（约40px 含"发送(S)"按钮）
    btn_bar_h = 40
    box_x = win.left + SIDEBAR
    box_y = win.top + win.height - INPUT_H
    box_w = win.width - SIDEBAR
    box_h = INPUT_H - btn_bar_h
    img = pyautogui.screenshot(region=(box_x, box_y, box_w, box_h))
    enhancer = ImageEnhance.Contrast(img)
    img_enhanced = enhancer.enhance(1.5)
    result = await winocr.recognize_pil(img_enhanced, 'zh-Hans-CN')
    text = ' '.join(line.text.strip() for line in result.lines).strip()
    if len(text) < 5:
        print("[ok] 发送成功")
    else:
        print(f"[warn] 输入框可能仍有内容: {text[:50]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('用法: python wechat-send.py "消息内容"', file=sys.stderr)
        sys.exit(1)
    asyncio.run(send_message(sys.argv[1]))
