"""
T-418: wechat-send.py 输入动作通过 Executor 执行
"""
import importlib.util
import sys
import types
from pathlib import Path

import pytest

WECHAT_SEND_PATH = Path(__file__).resolve().parents[1] / "wechat-send.py"


@pytest.fixture
def wechat_send_module(monkeypatch):
    pyautogui_stub = types.SimpleNamespace(
        click=lambda *a, **kw: None,
        hotkey=lambda *a, **kw: None,
        press=lambda *a, **kw: None,
        screenshot=lambda *a, **kw: None,
        FAILSAFE=True,
        PAUSE=0.1,
    )
    gw_stub = types.SimpleNamespace(getAllWindows=lambda: [])
    pil_enhance_stub = types.SimpleNamespace(
        Contrast=lambda img: types.SimpleNamespace(enhance=lambda _: img)
    )
    winocr_stub = types.SimpleNamespace(recognize_pil=None)

    monkeypatch.setitem(sys.modules, "pyautogui", pyautogui_stub)
    monkeypatch.setitem(sys.modules, "pygetwindow", gw_stub)
    monkeypatch.setitem(sys.modules, "winocr", winocr_stub)
    monkeypatch.setitem(
        sys.modules,
        "PIL",
        types.SimpleNamespace(ImageEnhance=pil_enhance_stub),
    )

    # wechat-send.py 模块级会执行 sys.stdout = io.TextIOWrapper(sys.stdout.buffer, ...)
    # 如果包住 pytest 的 capture buffer，teardown 时会触发 "I/O operation on closed file"
    # 解法：先把 sys.stdout 换成安全的 BytesIO wrapper，让模块包住它
    import io as _io
    safe_stdout = _io.TextIOWrapper(_io.BytesIO(), encoding='utf-8')
    monkeypatch.setattr(sys, 'stdout', safe_stdout)

    spec = importlib.util.spec_from_file_location("wechat_send", WECHAT_SEND_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_executor_importable_from_core_runtime():
    """build_executor 应从 core.runtime 直接可导入，不依赖 desktop.py"""
    from core.runtime import build_executor
    from core.executor import Executor

    executor = build_executor()
    assert isinstance(executor, Executor)
    assert executor.input_adapter is not None


async def _fake_recognize(img, lang):
    """模拟 winocr.recognize_pil 返回空结果（输入框已清空）"""
    return types.SimpleNamespace(lines=[])


async def test_send_message_uses_executor_for_click_hotkey_press(monkeypatch, wechat_send_module):
    """send_message 应通过 executor 调用 click / hotkey / press，不直接调用 pyautogui"""
    calls = []

    class FakeExecutor:
        def click(self, x, y, safety=None):
            calls.append(("click", x, y))
            return {"ok": True, "action": "click", "point": [x, y], "context": {}}

        def hotkey(self, *keys, safety=None):
            calls.append(("hotkey", keys))
            return {"ok": True, "action": "hotkey", "keys": list(keys)}

        def press(self, key, safety=None):
            calls.append(("press", key))
            return {"ok": True, "action": "press", "key": key}

    # 构造一个假窗口
    fake_win = types.SimpleNamespace(
        title="微信", width=800, height=600,
        left=0, top=0,
        activate=lambda: None,
    )
    monkeypatch.setattr(wechat_send_module, "find_wechat_window", lambda: fake_win)
    monkeypatch.setattr(wechat_send_module, "copy_to_clipboard", lambda text: None)
    monkeypatch.setattr(wechat_send_module, "build_executor", lambda: FakeExecutor())

    import sys as _sys
    monkeypatch.setattr(_sys.modules["winocr"], "recognize_pil", _fake_recognize)

    await wechat_send_module.send_message("hello")

    actions = [c[0] for c in calls]
    assert "click" in actions
    assert "hotkey" in actions
    assert "press" in actions

    hotkey_call = next(c for c in calls if c[0] == "hotkey")
    assert set(hotkey_call[1]) == {"ctrl", "v"}

    press_call = next(c for c in calls if c[0] == "press")
    assert press_call[1] == "enter"
