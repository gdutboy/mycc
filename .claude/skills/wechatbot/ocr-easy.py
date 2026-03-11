#!/usr/bin/env python3
"""
Windows OCR 脚本 - 使用 EasyOCR
基于 PyTorch，无需额外依赖

用法:
  python ocr-easy.py --screen           # 全屏 OCR
  python ocr-easy.py --cursor          # 鼠标附近 OCR
  python ocr-easy.py --bbox            # JSON 格式输出
"""

import argparse
import json
import sys
import time
from pathlib import Path

try:
    import pyautogui
    from mss import mss
    from PIL import Image
    import numpy as np
    import easyocr
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请运行: pip install pyautogui mss easyocr pillow")
    sys.exit(1)


# 全局 Reader 实例（单例模式）
_reader = None
_reader_languages = None


def get_reader(languages=['ch_sim', 'en']):
    """获取或创建全局 Reader 实例"""
    global _reader, _reader_languages

    # 如果已存在且语言相同，直接返回
    if _reader is not None and _reader_languages == languages:
        return _reader

    # 检查本地模型是否存在
    model_dir = Path.home() / '.EasyOCR' / 'model'
    if model_dir.exists():
        print(f"[EasyOCR] 使用本地缓存模型: {model_dir}", file=sys.stderr)
    else:
        print(f"[EasyOCR] 本地模型不存在，将自动下载到: {model_dir}", file=sys.stderr)

    # 创建新的 Reader
    print(f"[EasyOCR] 初始化 Reader (语言: {', '.join(languages)})...", file=sys.stderr)
    _reader = easyocr.Reader(languages, gpu=False)
    _reader_languages = languages

    return _reader


def get_cursor_position():
    """获取鼠标位置"""
    return pyautogui.position()


def ocr_region(x, y, width, height, languages=['ch_sim', 'en']):
    """OCR 指定屏幕区域（重用全局 Reader）"""
    # 截图
    with mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        screenshot = sct.grab(monitor)

    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

    # 转换为 numpy array
    img_array = np.array(img)

    # 获取复用的 Reader
    reader = get_reader(languages)

    # 执行 OCR
    results = reader.readtext(img_array)

    # 转换为统一格式
    items = []
    for (bbox, text, confidence) in results:
        # bbox 格式: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        bbox_x = int(min(x_coords))
        bbox_y = int(min(y_coords))
        bbox_w = int(max(x_coords) - bbox_x)
        bbox_h = int(max(y_coords) - bbox_y)

        # 计算中心点
        center_x = bbox_x + bbox_w // 2
        center_y = bbox_y + bbox_h // 2

        items.append({
            "text": text,
            "confidence": confidence,
            "bbox": [bbox_x, bbox_y, bbox_w, bbox_h],
            "center": [center_x, center_y]
        })

    return items


def print_ocr_results(items, show_cursor=True):
    """打印 OCR 结果"""
    if show_cursor:
        x, y = get_cursor_position()
        print(f"cursor: ({x},{y})", end="  ", flush=True)

    for item in items:
        text = item.get("text", item) if isinstance(item, dict) else item
        conf = item.get("confidence", 1.0) if isinstance(item, dict) else 1.0
        bbox = item.get("bbox", [0, 0, 0, 0]) if isinstance(item, dict) else [0, 0, 0, 0]
        cx, cy = (
            item.get("center", [bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2])
            if isinstance(item, dict)
            else [0, 0]
        )
        print(f"  [{conf:.2f}] {text} @ ({cx},{cy})")


def main():
    parser = argparse.ArgumentParser(description="Windows OCR - EasyOCR 版本（基于 PyTorch）")
    parser.add_argument("--screen", action="store_true", help="全屏 OCR")
    parser.add_argument("--cursor", action="store_true", help="鼠标附近 OCR")
    parser.add_argument("--size", default="300x200", help="区域大小 (宽x高)")
    parser.add_argument("--bbox", action="store_true", help="输出 JSON 坐标")
    parser.add_argument("image", nargs="?", help="OCR 指定图片")

    args = parser.parse_args()

    w, h = map(int, args.size.split("x"))

    if args.image:
        # OCR 图片文件
        print(f"OCR 图片: {args.image}")

        reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        results = reader.readtext(args.image)

        if results:
            for (bbox, text, confidence) in results:
                print(f"  [{confidence:.2f}] {text}")

    elif args.screen:
        # 全屏 OCR
        screen_w, screen_h = pyautogui.size()
        print(f"全屏 OCR ({screen_w}x{screen_h})...")
        start = time.time()

        items = ocr_region(0, 0, screen_w, screen_h)

        if args.bbox:
            result = {"cursor": list(get_cursor_position()), "items": items}
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            for item in items:
                print(item.get("text", ""))

        elapsed = (time.time() - start) * 1000
        print(f"耗时: {elapsed:.0f}ms", file=sys.stderr)

    elif args.cursor:
        # 鼠标附近 OCR
        x, y = get_cursor_position()
        # 居中区域
        x = max(0, x - w // 2)
        y = max(0, y - h // 2)

        start = time.time()

        items = ocr_region(x, y, w, h)
        elapsed = (time.time() - start) * 1000

        if args.bbox:
            result = {
                "cursor": list(get_cursor_position()),
                "elapsed_ms": int(elapsed),
                "items": items,
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            x, y = get_cursor_position()
            print(f"cursor: ({x},{y})  ocr: {elapsed:.0f}ms")
            for item in items:
                text = item.get("text", "")
                if text:
                    print(f"  {text}")

            if not items:
                print("  [无文字]")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
