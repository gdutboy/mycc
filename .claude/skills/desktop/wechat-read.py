#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
wechat-read.py — 读取微信当前聊天内容（Windows 版，使用 Windows 原生 OCR）
用法: python wechat-read.py [--bbox]
输出: OCR 识别的聊天文字
"""
import sys
import os
import io
import json
import time
import asyncio
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pyautogui
import pygetwindow as gw

try:
    import winocr
except ImportError:
    print("[error] winocr 未安装，请运行: pip install winocr", file=sys.stderr)
    sys.exit(1)

# 微信 Windows 版 UI 参数（可通过环境变量覆盖）
SIDEBAR = int(os.environ.get("WECHAT_SIDEBAR", 320))
TITLE_H = int(os.environ.get("WECHAT_TITLE_H", 60))
INPUT_H = int(os.environ.get("WECHAT_INPUT_H", 160))


def find_wechat_window():
    """查找微信窗口"""
    for w in gw.getAllWindows():
        if w.title == "微信" and w.width > 400:
            return w
    return None


async def read_chat(bbox_mode=False):
    """读取聊天内容"""
    win = find_wechat_window()
    if not win:
        print("[error] 微信窗口未找到", file=sys.stderr)
        sys.exit(1)

    # 激活微信
    try:
        win.activate()
        time.sleep(0.5)
    except Exception:
        pass

    # 计算聊天内容区域
    x = win.left + SIDEBAR
    y = win.top + TITLE_H
    w = win.width - SIDEBAR
    h = win.height - TITLE_H - INPUT_H

    if w <= 0 or h <= 0:
        print(f"[error] 窗口尺寸异常: {win.width}x{win.height}", file=sys.stderr)
        sys.exit(1)

    # 截取聊天区域
    img = pyautogui.screenshot(region=(x, y, w, h))

    # 增强对比度（提高灰色气泡文字识别率）
    from PIL import ImageEnhance
    img = ImageEnhance.Contrast(img).enhance(2.0)

    # Windows 原生 OCR（中文）
    result = await winocr.recognize_pil(img, 'zh-Hans-CN')

    if bbox_mode:
        items = []
        for line in result.lines:
            for word in line.words:
                # winocr 的 word 有 bounding_rect 属性
                br = word.bounding_rect
                items.append({
                    "text": word.text,
                    "bbox": [int(br.x) + x, int(br.y) + y, int(br.width), int(br.height)],
                    "center": [int(br.x + br.width / 2) + x, int(br.y + br.height / 2) + y]
                })
        output = {
            "window": {"x": win.left, "y": win.top, "w": win.width, "h": win.height},
            "chat_region": {"x": x, "y": y, "w": w, "h": h},
            "count": len(items),
            "items": items
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        # 输出纯文字，每行一条，去除多余空格
        lines = []
        for line in result.lines:
            text = line.text.replace(' ', '')  # 去除 Windows OCR 的字符间空格
            if text:
                lines.append(text)
        print('\n'.join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="读取微信聊天内容")
    parser.add_argument("--bbox", action="store_true", help="返回 JSON 包围盒")
    args = parser.parse_args()
    asyncio.run(read_chat(bbox_mode=args.bbox))
