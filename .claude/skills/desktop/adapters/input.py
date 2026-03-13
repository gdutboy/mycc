import pyautogui


KEY_MAP = {
    "enter": "enter",
    "return": "enter",
    "tab": "tab",
    "escape": "esc",
    "esc": "esc",
    "ctrl": "ctrl",
    "alt": "alt",
    "shift": "shift",
    "win": "win",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "delete": "delete",
    "backspace": "backspace",
}


def click(x=None, y=None, button="left", double=False):
    if x is not None and y is not None:
        pyautogui.click(x, y, clicks=2 if double else 1, button=button)
        return f"点击 ({x}, {y})"

    pyautogui.click(clicks=2 if double else 1, button=button)
    return "点击当前位置"


def press_key(key):
    normalized = KEY_MAP.get(key.lower(), key)
    pyautogui.press(normalized)
    return f"按下: {normalized}"


def hotkey(*keys):
    pyautogui.hotkey(*keys)
    return f"按下组合键: {'+'.join(keys)}"
