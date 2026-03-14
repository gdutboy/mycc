import os
import subprocess
import tempfile
import time

import pyautogui

from adapters import input as input_adapter
from core.executor import Executor


class _InputAdapterWrapper:
    """将 adapters/input.py 模块函数封装为 Executor 所需的对象接口。"""

    def click(self, x=None, y=None, button="left", double=False):
        return input_adapter.click(x=x, y=y, button=button, double=double)

    def move_to(self, x, y):
        pyautogui.moveTo(x, y)

    def scroll(self, clicks):
        return input_adapter.scroll(clicks)

    def type_text(self, text):
        tmp = os.path.join(tempfile.gettempdir(), "desktop_clip.txt")
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(text)
        subprocess.run(
            ['powershell', '-command',
             f'Get-Content -Path "{tmp}" -Encoding UTF8 -Raw | Set-Clipboard'],
            capture_output=True,
        )
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)

    def press_key(self, key):
        return input_adapter.press_key(key)

    def hotkey(self, *keys):
        return input_adapter.hotkey(*keys)


def build_executor():
    """组装并返回带真实 input adapter 的 Executor。"""
    return Executor(input_adapter=_InputAdapterWrapper())
