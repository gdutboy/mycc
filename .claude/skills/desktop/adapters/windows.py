import ctypes
import json
import time

import pygetwindow as gw


def get_user32():
    return ctypes.windll.user32


def list_windows():
    windows = gw.getAllWindows()
    result = []
    for window in windows:
        if window.title:
            result.append(
                {
                    "title": window.title,
                    "position": list(window.box),
                    "active": window.isActive,
                }
            )
    return json.dumps(result, ensure_ascii=False, indent=2)


def get_active_window():
    window = gw.getActiveWindow()
    if not window:
        return "{}"

    return json.dumps(
        {
            "title": window.title,
            "position": list(window.box),
            "size": [window.width, window.height],
        },
        ensure_ascii=False,
        indent=2,
    )


def activate_window(title):
    user32 = get_user32()
    windows = gw.getAllWindows()
    for window in windows:
        if title.lower() in window.title.lower():
            user32.ShowWindow(window._hWnd, 9)
            time.sleep(0.3)
            user32.SetForegroundWindow(window._hWnd)
            time.sleep(0.3)
            return f"已激活窗口: {window.title}"
    return f"未找到窗口: {title}"
