import importlib.util
import sys
import types
from pathlib import Path

import pytest


DESKTOP_PATH = Path(__file__).resolve().parents[1] / "desktop.py"


@pytest.fixture
def desktop_module(monkeypatch):
    pyautogui_stub = types.SimpleNamespace(
        size=lambda: (1920, 1080),
        screenshot=lambda *args, **kwargs: None,
        position=lambda: (0, 0),
        moveTo=lambda *args, **kwargs: None,
        click=lambda *args, **kwargs: None,
        rightClick=lambda *args, **kwargs: None,
        hotkey=lambda *args, **kwargs: None,
        press=lambda *args, **kwargs: None,
    )
    gw_stub = types.SimpleNamespace(getAllWindows=lambda: [], getActiveWindow=lambda: None)
    pil_image_stub = types.SimpleNamespace(frombytes=lambda *args, **kwargs: None)
    pil_draw_stub = types.SimpleNamespace()
    pil_enhance_stub = types.SimpleNamespace(Contrast=lambda image: types.SimpleNamespace(enhance=lambda _: image))
    mss_module = types.ModuleType("mss")
    mss_module.mss = lambda: types.SimpleNamespace(monitors=[{}], grab=lambda monitor: None)
    mss_tools_module = types.ModuleType("mss.tools")
    winocr_stub = types.SimpleNamespace(recognize_pil=None)

    monkeypatch.setitem(sys.modules, "pyautogui", pyautogui_stub)
    monkeypatch.setitem(sys.modules, "pygetwindow", gw_stub)
    monkeypatch.setitem(sys.modules, "winocr", winocr_stub)
    monkeypatch.setitem(sys.modules, "mss", mss_module)
    monkeypatch.setitem(sys.modules, "mss.tools", mss_tools_module)
    monkeypatch.setitem(
        sys.modules,
        "PIL",
        types.SimpleNamespace(Image=pil_image_stub, ImageDraw=pil_draw_stub, ImageEnhance=pil_enhance_stub),
    )

    spec = importlib.util.spec_from_file_location("desktop_legacy", DESKTOP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_screenshot_delegates_to_screen_adapter(monkeypatch, desktop_module):
    calls = []

    def fake_capture_screen(region=None, save_path=None):
        calls.append({"region": region, "save_path": save_path})
        return "fake-image"

    monkeypatch.setattr(desktop_module.screen_adapter, "capture_screen", fake_capture_screen)

    result = desktop_module.screenshot("screen.png", region=(1, 2, 30, 40))

    assert result == "fake-image"
    assert calls == [{"region": (1, 2, 30, 40), "save_path": "screen.png"}]


def test_click_delegates_to_input_adapter(monkeypatch, desktop_module):
    calls = []
    monkeypatch.setattr(
        desktop_module.input_adapter,
        "click",
        lambda x=None, y=None, button="left", double=False: calls.append((x, y, button, double)) or "clicked",
    )

    result = desktop_module.click(10, 20, button="right", double=True)

    assert result == "clicked"
    assert calls == [(10, 20, "right", True)]


def test_press_key_delegates_to_input_adapter(monkeypatch, desktop_module):
    calls = []
    monkeypatch.setattr(desktop_module.input_adapter, "press_key", lambda key: calls.append(key) or "pressed")

    result = desktop_module.press_key("enter")

    assert result == "pressed"
    assert calls == ["enter"]


def test_hotkey_delegates_to_input_adapter(monkeypatch, desktop_module):
    calls = []
    monkeypatch.setattr(desktop_module.input_adapter, "hotkey", lambda *keys: calls.append(keys) or "combo")

    result = desktop_module.hotkey("ctrl", "shift", "s")

    assert result == "combo"
    assert calls == [("ctrl", "shift", "s")]


def test_list_windows_delegates_to_windows_adapter(monkeypatch, desktop_module):
    monkeypatch.setattr(desktop_module.windows_adapter, "list_windows", lambda: "[]")

    assert desktop_module.list_windows() == "[]"


def test_get_active_window_delegates_to_windows_adapter(monkeypatch, desktop_module):
    monkeypatch.setattr(desktop_module.windows_adapter, "get_active_window", lambda: '{"title": "微信"}')

    assert desktop_module.get_active_window() == '{"title": "微信"}'


def test_activate_window_delegates_to_windows_adapter(monkeypatch, desktop_module):
    calls = []
    monkeypatch.setattr(desktop_module.windows_adapter, "activate_window", lambda title: calls.append(title) or "ok")

    result = desktop_module.activate_window("QQ")

    assert result == "ok"
    assert calls == ["QQ"]
