#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
wechat-send-file.py — 发送文件/图片到微信（Windows 版）
用法: python wechat-send-file.py /path/to/file
"""
import sys
import os
import io
import time
import subprocess
import asyncio

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pyautogui
import pygetwindow as gw
from PIL import ImageEnhance

try:
    import winocr
except ImportError:
    print("[error] winocr 未安装，请运行: pip install winocr", file=sys.stderr)
    sys.exit(1)

SIDEBAR = int(os.environ.get("WECHAT_SIDEBAR", 320))
INPUT_H = int(os.environ.get("WECHAT_INPUT_H", 160))


def find_wechat_window():
    for w in gw.getAllWindows():
        if w.title == "微信" and w.width > 400:
            return w
    return None


def copy_file_to_clipboard(filepath):
    """通过 PowerShell 将文件复制到剪贴板"""
    abs_path = os.path.abspath(filepath)
    ps_script = f'''
$file = [System.Collections.Specialized.StringCollection]::new()
$file.Add("{abs_path}")
[System.Windows.Forms.Clipboard]::SetFileDropList($file)
'''
    subprocess.run(
        ['powershell', '-sta', '-command',
         'Add-Type -AssemblyName System.Windows.Forms;' + ps_script],
        capture_output=True
    )


async def send_file(filepath):
    if not os.path.isfile(filepath):
        print(f"[error] 文件不存在: {filepath}", file=sys.stderr)
        sys.exit(1)

    win = find_wechat_window()
    if not win:
        print("[error] 微信窗口未找到", file=sys.stderr)
        sys.exit(1)

    # 1. 激活微信
    try:
        win.activate()
        time.sleep(0.5)
    except Exception:
        pass

    # 2. 复制文件到剪贴板
    copy_file_to_clipboard(filepath)
    time.sleep(0.3)

    # 3. 点击输入框
    input_x = win.left + SIDEBAR + (win.width - SIDEBAR) // 2
    input_y = win.top + win.height - 50
    pyautogui.click(input_x, input_y)
    time.sleep(0.2)

    # 4. 粘贴 + 回车
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')

    # 5. 验证
    time.sleep(1.0)
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
        print("[ok] 文件发送成功")
    else:
        print(f"[warn] 输入框可能仍有内容: {text[:50]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('用法: python wechat-send-file.py /path/to/file', file=sys.stderr)
        sys.exit(1)
    asyncio.run(send_file(sys.argv[1]))
