#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Windows 桌面控制脚本
功能：截图、OCR（Windows 原生）、鼠标控制、键盘控制、窗口管理
"""
import sys
import os
import json
import argparse
import time
import io
import asyncio

# 修复 Windows 中文输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 尝试导入依赖，失败时给出友好提示
try:
    import pyautogui
    import pygetwindow as gw
    from PIL import Image, ImageDraw, ImageEnhance
    import mss
    import mss.tools
except ImportError as e:
    print(f"错误: 缺少依赖库 - {e}")
    print("请运行: pip install pyautogui Pillow pygetwindow mss winocr")
    sys.exit(1)

try:
    import winocr
except ImportError:
    print("错误: winocr 未安装，请运行: pip install winocr")
    sys.exit(1)


def get_screen_size():
    """获取屏幕尺寸"""
    return pyautogui.size()


def screenshot(filename=None, region=None):
    """
    截图

    Args:
        filename: 保存路径，None 则不保存
        region: (x, y, width, height) 区域截图，None 则全屏

    Returns:
        PIL Image 对象
    """
    # 优先使用 mss（更可靠，能捕获完整屏幕）
    try:
        import mss
        s = mss.mss()

        if region:
            # 区域截图
            monitor = {"left": region[0], "top": region[1], "width": region[2], "height": region[3]}
        else:
            # 全屏截图，使用 monitor 0（所有显示器合并）
            monitor = s.monitors[0]

        img_raw = s.grab(monitor)
        # mss 返回的是 BGRA，需要转换为 RGB
        img = Image.frombytes("RGB", img_raw.size, img_raw.bgra, "raw", "BGRX")
    except Exception as e:
        # 回退到 pyautogui
        print(f"mss 截图失败，使用 pyautogui: {e}")
        if region:
            img = pyautogui.screenshot(region=region)
        else:
            img = pyautogui.screenshot()

    if filename:
        img.save(filename)
        print(f"截图已保存: {filename}")

    return img


async def ocr_image(img, bbox=None, fast=False):
    """
    OCR 识别图片中的文字（Windows 原生 OCR）

    Args:
        img: PIL Image 对象
        bbox: (x, y, width, height) 只识别指定区域
        fast: 是否使用快速模式

    Returns:
        识别结果字符串
    """
    try:
        # 图片预处理：增强对比度
        enhancer = ImageEnhance.Contrast(img)
        img_enhanced = enhancer.enhance(2.0)

        if bbox:
            # bbox 是 (x, y, w, h)，crop 需要 (x1, y1, x2, y2)
            img_enhanced = img_enhanced.crop((bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]))

        result = await winocr.recognize_pil(img_enhanced, 'zh-Hans-CN')

        lines = []
        for line in result.lines:
            text = line.text.strip()
            if text:
                lines.append(text)

        return '\n'.join(lines)
    except Exception as e:
        print(f"OCR 错误: {e}")
        return ""


async def ocr_with_position(img, bbox=None):
    """
    OCR 识别并返回文字位置

    Returns:
        JSON 格式: {"items": [{"text": "...", "bbox": [x,y,w,h], "center": [x,y]}]}
    """
    try:
        # 图片预处理：增强对比度
        enhancer = ImageEnhance.Contrast(img)
        img_enhanced = enhancer.enhance(2.0)

        offset_x, offset_y = 0, 0
        if bbox:
            offset_x, offset_y = bbox[0], bbox[1]
            img_enhanced = img_enhanced.crop((bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]))

        result = await winocr.recognize_pil(img_enhanced, 'zh-Hans-CN')

        items = []
        for line in result.lines:
            for word in line.words:
                br = word.bounding_rect
                x, y, w, h = int(br.x), int(br.y), int(br.width), int(br.height)
                items.append({
                    "text": word.text,
                    "bbox": [x + offset_x, y + offset_y, w, h],
                    "center": [x + w // 2 + offset_x, y + h // 2 + offset_y]
                })

        return json.dumps({"items": items}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_cursor_position():
    """获取鼠标当前位置"""
    x, y = pyautogui.position()
    return f"cursor: ({x}, {y})"


def move_mouse(x, y):
    """移动鼠标到指定位置"""
    pyautogui.moveTo(x, y)
    return f"鼠标已移动到 ({x}, {y})"


def click(x=None, y=None, button='left', double=False):
    """点击鼠标

    Args:
        x, y: 点击位置，None 则点击当前位置
        button: left, right, middle
        double: 是否双击
    """
    if x is not None and y is not None:
        pyautogui.click(x, y, clicks=2 if double else 1, button=button)
        return f"点击 ({x}, {y})"
    else:
        pyautogui.click(clicks=2 if double else 1, button=button)
        return f"点击当前位置"


def right_click(x=None, y=None):
    """右键点击"""
    if x is not None and y is not None:
        pyautogui.rightClick(x, y)
        return f"右键点击 ({x}, {y})"
    else:
        pyautogui.rightClick()
        return "右键点击当前位置"


def type_text(text):
    """输入文字（通过临时文件+剪贴板，支持中文）"""
    import subprocess
    import tempfile
    # 写入临时文件，再用 PowerShell 读取并设置剪贴板
    tmp = os.path.join(tempfile.gettempdir(), "desktop_clip.txt")
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    subprocess.run(
        ['powershell', '-command',
         f'Get-Content -Path "{tmp}" -Encoding UTF8 -Raw | Set-Clipboard'],
        capture_output=True
    )
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)
    return f"已输入: {text}"


def press_key(key):
    """按键

    Args:
        key: enter, tab, escape, ctrl, alt, shift, win, 等
    """
    # 映射按键名称
    key_map = {
        'enter': 'enter',
        'return': 'enter',
        'tab': 'tab',
        'escape': 'esc',
        'esc': 'esc',
        'ctrl': 'ctrl',
        'alt': 'alt',
        'shift': 'shift',
        'win': 'win',
        'up': 'up',
        'down': 'down',
        'left': 'left',
        'right': 'right',
        'delete': 'delete',
        'backspace': 'backspace',
    }

    key = key_map.get(key.lower(), key)
    pyautogui.press(key)
    return f"按下: {key}"


def hotkey(*keys):
    """组合键

    Examples:
        hotkey('ctrl', 'c')  # 复制
        hotkey('ctrl', 'v')  # 粘贴
        hotkey('alt', 'f4')  # 关闭窗口
    """
    pyautogui.hotkey(*keys)
    return f"按下组合键: {'+'.join(keys)}"


def list_windows():
    """列出所有窗口"""
    try:
        windows = gw.getAllWindows()
        result = []
        for w in windows:
            if w.title:
                result.append({
                    "title": w.title,
                    "position": list(w.box),
                    "active": w.isActive
                })
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_active_window():
    """获取当前活动窗口"""
    try:
        w = gw.getActiveWindow()
        if w:
            return json.dumps({
                "title": w.title,
                "position": list(w.box),
                "size": [w.width, w.height]
            }, ensure_ascii=False, indent=2)
        return "{}"
    except Exception as e:
        return json.dumps({"error": str(e)})


def activate_window(title):
    """激活指定窗口（模糊匹配，支持最小化窗口恢复）"""
    import ctypes
    user32 = ctypes.windll.user32

    try:
        windows = gw.getAllWindows()
        for w in windows:
            if title.lower() in w.title.lower():
                hwnd = w._hWnd
                # SW_RESTORE = 9，恢复最小化窗口
                user32.ShowWindow(hwnd, 9)
                time.sleep(0.3)
                # SetForegroundWindow 激活到前台
                user32.SetForegroundWindow(hwnd)
                time.sleep(0.3)
                return f"已激活窗口: {w.title}"
        return f"未找到窗口: {title}"
    except Exception as e:
        return f"错误: {e}"


async def cursor_ocr(size=(300, 200)):
    """鼠标附近的 OCR（触觉模式）"""
    x, y = pyautogui.position()

    # 获取鼠标附近的区域
    w, h = size
    region = (max(0, x - w // 2), max(0, y - h // 2), w, h)

    img = screenshot(region=region)
    text = await ocr_image(img)

    return f"cursor: ({x}, {y})  ocr: {text[:100]}"


async def find_text(text, region=None):
    """在屏幕上查找文字并返回位置"""
    try:
        if region:
            img = screenshot(region=region)
        else:
            img = screenshot()

        # 图片预处理：增强对比度
        enhancer = ImageEnhance.Contrast(img)
        img_enhanced = enhancer.enhance(2.0)

        result = await winocr.recognize_pil(img_enhanced, 'zh-Hans-CN')

        offset_x = region[0] if region else 0
        offset_y = region[1] if region else 0

        for line in result.lines:
            for word in line.words:
                if text.lower() in word.text.lower():
                    br = word.bounding_rect
                    x, y = int(br.x), int(br.y)
                    w, h = int(br.width), int(br.height)
                    return json.dumps({
                        "found": True,
                        "text": word.text,
                        "bbox": [x + offset_x, y + offset_y, w, h],
                        "center": [x + w // 2 + offset_x, y + h // 2 + offset_y]
                    }, ensure_ascii=False)

        return json.dumps({"found": False})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def find_icon(icon_name, row=None):
    """通过图标名称查找桌面图标位置

    Args:
        icon_name: 图标名称（如"飞书"、"微信"）
        row: 指定行号（0开始），None则自动查找

    Returns:
        JSON: 找到的图标位置信息
    """
    try:
        # 先最小化所有窗口，回到桌面
        pyautogui.hotkey('win', 'd')
        time.sleep(0.3)

        # 截取全屏
        s = mss.mss()
        monitor = s.monitors[0]
        img_raw = s.grab(monitor)
        img = Image.frombytes("RGB", img_raw.size, img_raw.bgra, "raw", "BGRX")

        result = await winocr.recognize_pil(img, 'zh-Hans-CN')

        matches = []
        for line in result.lines:
            for word in line.words:
                if icon_name.lower() in word.text.lower():
                    br = word.bounding_rect
                    x, y, w, h = int(br.x), int(br.y), int(br.width), int(br.height)
                    matches.append({
                        "text": word.text,
                        "bbox": [x, y, w, h],
                        "center": [x + w // 2, y + h // 2]
                    })

        if not matches:
            return json.dumps({"found": False, "suggestion": "未找到图标，请尝试：1. 确保桌面图标名称正确 2. 先移动鼠标到目标图标上，用 --cursor-pos 获取位置"})

        # 如果指定了行号，尝试通过Y坐标匹配
        if row is not None:
            target_y = row * 100 + 100
            for match in matches:
                if abs(match['center'][1] - target_y) < 50:
                    return json.dumps({
                        "found": True,
                        "icon": icon_name,
                        "row": row,
                        "text": match['text'],
                        "bbox": match['bbox'],
                        "center": match['center'],
                        "tip": f"建议双击坐标 {match['center'][0]} {match['center'][1]} 启动"
                    }, ensure_ascii=False)

        match = matches[0]
        estimated_row = (match['center'][1] - 100) // 100 if match['center'][1] > 100 else 0

        return json.dumps({
            "found": True,
            "icon": icon_name,
            "text": match['text'],
            "bbox": match['bbox'],
            "center": match['center'],
            "estimated_row": estimated_row,
            "total_matches": len(matches),
            "tip": f"建议双击坐标 {match['center'][0]} {match['center'][1]} 启动"
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)})


async def async_main(args):
    """异步主函数（处理需要 await 的 OCR 调用）"""
    # 执行命令
    if args.screenshot or (args.ocr and not args.cursor):
        img = screenshot(args.screenshot, args.region)
        if args.ocr:
            # region 已在截图时裁剪，不再传给 OCR（避免二次裁剪）
            if args.bbox:
                print(await ocr_with_position(img))
            else:
                print(await ocr_image(img))

    elif args.active_screenshot:
        active = gw.getActiveWindow()
        if active:
            time.sleep(0.2)
            region = (active.left, active.top, active.width, active.height)
            img = screenshot(args.active_screenshot, region=region)
            if args.ocr:
                if args.bbox:
                    print(await ocr_with_position(img))
                else:
                    print(await ocr_image(img))
        else:
            print("错误: 没有活动窗口")

    elif args.cursor:
        print(await cursor_ocr(tuple(args.size)))

    elif args.cursor_pos:
        print(get_cursor_position())

    elif args.move:
        print(move_mouse(args.move[0], args.move[1]))

    elif args.click:
        print(click(args.click[0], args.click[1]))

    elif args.double_click:
        print(click(args.double_click[0], args.double_click[1], double=True))

    elif args.right_click:
        print(right_click(args.right_click[0], args.right_click[1]))

    elif args.type:
        print(type_text(args.type))

    elif args.press:
        print(press_key(args.press))

    elif args.hotkey:
        print(hotkey(*args.hotkey))

    elif args.windows:
        print(list_windows())

    elif args.active_window:
        print(get_active_window())

    elif args.activate:
        print(activate_window(args.activate))

    elif args.find:
        print(await find_text(args.find, args.region and tuple(args.region)))

    elif args.find_icon:
        print(await find_icon(args.find_icon, args.icon_row))

    else:
        print(f"屏幕尺寸: {get_screen_size()}")
        print("使用 --help 查看所有选项")


def main():
    parser = argparse.ArgumentParser(description='Windows 桌面控制工具')
    parser.add_argument('--screenshot', '-s', metavar='FILE', help='截图保存路径')
    parser.add_argument('--active-screenshot', '-a', metavar='FILE', help='截取活动窗口图像')
    parser.add_argument('--region', '-r', nargs=4, type=int, metavar='X Y W H', help='区域截图')
    parser.add_argument('--ocr', '-o', action='store_true', help='OCR 识别')
    parser.add_argument('--bbox', '-b', action='store_true', help='返回文字包围盒')
    parser.add_argument('--cursor', '-c', action='store_true', help='鼠标附近 OCR')
    parser.add_argument('--cursor-pos', action='store_true', help='获取鼠标位置')
    parser.add_argument('--move', '-m', nargs=2, type=int, metavar='X Y', help='移动鼠标')
    parser.add_argument('--click', nargs=2, type=int, metavar='X Y', help='点击')
    parser.add_argument('--double-click', nargs=2, type=int, metavar='X Y', help='双击')
    parser.add_argument('--right-click', nargs=2, type=int, metavar='X Y', help='右键点击')
    parser.add_argument('--type', '-t', metavar='TEXT', help='输入文字')
    parser.add_argument('--press', '-p', metavar='KEY', help='按键')
    parser.add_argument('--hotkey', nargs='+', metavar='KEY', help='组合键')
    parser.add_argument('--windows', '-w', action='store_true', help='列出所有窗口')
    parser.add_argument('--active-window', action='store_true', help='获取活动窗口')
    parser.add_argument('--activate', metavar='TITLE', help='激活窗口')
    parser.add_argument('--find', '-f', metavar='TEXT', help='查找文字位置')
    parser.add_argument('--find-icon', metavar='NAME', help='查找桌面图标位置（自动最小化窗口）')
    parser.add_argument('--icon-row', type=int, metavar='N', help='指定图标所在行（0开始）')
    parser.add_argument('--size', nargs=2, type=int, default=[300, 200], help='OCR 区域大小')

    args = parser.parse_args()

    # 设置 pyautogui 安全
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1

    asyncio.run(async_main(args))


if __name__ == '__main__':
    main()
