#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
wechat-monitor.py — 微信聊天监控（Windows 版）
用法: python wechat-monitor.py [关键词，默认 MYCC]
后台: pythonw wechat-monitor.py &
输出: 检测到触发词时写入临时文件
"""
import sys
import os
import io
import json
import time
import hashlib
import tempfile
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

# UI 参数
SIDEBAR = int(os.environ.get("WECHAT_SIDEBAR", 320))
TITLE_H = int(os.environ.get("WECHAT_TITLE_H", 60))
INPUT_H = int(os.environ.get("WECHAT_INPUT_H", 160))

# 监控参数
POLL = int(os.environ.get("WECHAT_POLL", 5))
COOLDOWN = int(os.environ.get("WECHAT_COOLDOWN", 20))
TRIGGER_FILE = os.path.join(tempfile.gettempdir(), "wechat-trigger")
LATEST_FILE = os.path.join(tempfile.gettempdir(), "wechat-latest.txt")


def find_wechat_window():
    for w in gw.getAllWindows():
        if w.title == "微信" and w.width > 400:
            return w
    return None


def md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


async def ocr_chat_region(win):
    """截取并 OCR 聊天区域（不激活窗口）"""
    x = win.left + SIDEBAR
    y = win.top + TITLE_H
    w = win.width - SIDEBAR
    h = win.height - TITLE_H - INPUT_H

    if w <= 0 or h <= 0:
        return None

    img = pyautogui.screenshot(region=(x, y, w, h))
    enhancer = ImageEnhance.Contrast(img)
    img_enhanced = enhancer.enhance(1.5)

    result = await winocr.recognize_pil(img_enhanced, 'zh-Hans-CN')
    lines = []
    for line in result.lines:
        text = line.text.strip()
        if text:
            lines.append(text)
    return '\n'.join(lines)


async def monitor(keyword="MYCC"):
    last_hash = ""
    last_trigger_hash = ""
    warmup = True
    last_trigger_time = 0

    print(f"[monitor] 启动微信监控 {time.strftime('%H:%M:%S')}")
    print(f"[monitor] 监听关键词: {keyword}")
    print(f"[monitor] 触发文件: {TRIGGER_FILE}")
    print(f"[monitor] 轮询间隔: {POLL}s")

    while True:
        win = find_wechat_window()
        if not win:
            time.sleep(POLL)
            continue

        result = await ocr_chat_region(win)
        if result is None:
            time.sleep(POLL)
            continue

        current_hash = md5(result)

        if current_hash != last_hash:
            # 内容变化
            with open(LATEST_FILE, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"[monitor] 内容变化 {time.strftime('%H:%M:%S')}")

            # 检查触发关键词
            trigger_lines = [line for line in result.split('\n') if keyword.upper() in line.upper()]
            if trigger_lines:
                trigger_text = '\n'.join(trigger_lines)
                trigger_hash = md5(trigger_text)

                if warmup:
                    print(f"[monitor] 预热完成，记录现有 @{keyword} 状态")
                    last_trigger_hash = trigger_hash
                    warmup = False
                elif trigger_hash != last_trigger_hash:
                    now = time.time()
                    if (now - last_trigger_time) >= COOLDOWN:
                        print(f"\n[monitor] ====== @{keyword} 触发! {time.strftime('%H:%M:%S')} ======")
                        # 原子写入
                        tmp = TRIGGER_FILE + ".tmp"
                        with open(tmp, 'w', encoding='utf-8') as f:
                            f.write(result)
                        os.replace(tmp, TRIGGER_FILE)
                        print(result)
                        print(f"[monitor] 已写入 {TRIGGER_FILE}")
                        last_trigger_time = now
                    else:
                        remaining = int(COOLDOWN - (now - last_trigger_time))
                        print(f"[monitor] 冷却中，跳过 ({remaining}s 后恢复)")
                    last_trigger_hash = trigger_hash

            last_hash = current_hash

        time.sleep(POLL)


if __name__ == "__main__":
    keyword = sys.argv[1] if len(sys.argv) > 1 else "MYCC"
    asyncio.run(monitor(keyword))
