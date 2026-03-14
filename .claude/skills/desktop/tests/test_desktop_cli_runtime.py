"""
T-417: desktop CLI 通过 Executor 执行输入类动作
"""
import argparse
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

DESKTOP_PATH = Path(__file__).resolve().parents[1] / "desktop.py"


@pytest.fixture
def desktop_module(monkeypatch):
    pyautogui_stub = types.SimpleNamespace(
        size=lambda: (1920, 1080),
        screenshot=lambda *a, **kw: None,
        position=lambda: (0, 0),
        moveTo=lambda *a, **kw: None,
        click=lambda *a, **kw: None,
        rightClick=lambda *a, **kw: None,
        hotkey=lambda *a, **kw: None,
        press=lambda *a, **kw: None,
        FAILSAFE=True,
        PAUSE=0.1,
    )
    gw_stub = types.SimpleNamespace(getAllWindows=lambda: [], getActiveWindow=lambda: None)
    pil_enhance_stub = types.SimpleNamespace(
        Contrast=lambda image: types.SimpleNamespace(enhance=lambda _: image)
    )
    mss_module = types.ModuleType("mss")
    mss_module.mss = lambda: types.SimpleNamespace(monitors=[{}], grab=lambda m: None)
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
        types.SimpleNamespace(
            Image=types.SimpleNamespace(frombytes=lambda *a, **kw: None),
            ImageDraw=types.SimpleNamespace(),
            ImageEnhance=pil_enhance_stub,
        ),
    )

    spec = importlib.util.spec_from_file_location("desktop_cli_runtime", DESKTOP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_args(**kwargs):
    defaults = dict(
        screenshot=None, active_screenshot=None, region=None, ocr=False, bbox=False,
        cursor=False, cursor_pos=False, move=None, click=None, double_click=None,
        right_click=None, type=None, press=None, hotkey=None,
        windows=False, active_window=False, activate=None,
        find=None, find_icon=None, icon_row=None, size=[300, 200],
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class FakeExecutor:
    def __init__(self):
        self.calls = []

    def click(self, x, y, safety=None):
        self.calls.append(("click", x, y))
        return {"ok": True, "action": "click", "point": [x, y], "context": {}}

    def double_click(self, x, y, safety=None):
        self.calls.append(("double_click", x, y))
        return {"ok": True, "action": "double_click", "point": [x, y]}

    def right_click(self, x, y, safety=None):
        self.calls.append(("right_click", x, y))
        return {"ok": True, "action": "right_click", "point": [x, y]}

    def move(self, x, y):
        self.calls.append(("move", x, y))
        return {"ok": True, "action": "move", "point": [x, y]}

    def type(self, text, safety=None):
        self.calls.append(("type", text))
        return {"ok": True, "action": "type", "input_length": len(text), "context": {}}

    def press(self, key, safety=None):
        self.calls.append(("press", key))
        return {"ok": True, "action": "press", "key": key}

    def hotkey(self, *keys, safety=None):
        self.calls.append(("hotkey", keys))
        return {"ok": True, "action": "hotkey", "keys": list(keys)}


@pytest.mark.asyncio
async def test_click_routes_through_executor(monkeypatch, desktop_module, capsys):
    fake = FakeExecutor()
    monkeypatch.setattr(desktop_module, "build_executor", lambda: fake)

    await desktop_module.async_main(make_args(click=[10, 20]))

    assert fake.calls == [("click", 10, 20)]
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True
    assert out["action"] == "click"


@pytest.mark.asyncio
async def test_double_click_routes_through_executor(monkeypatch, desktop_module, capsys):
    fake = FakeExecutor()
    monkeypatch.setattr(desktop_module, "build_executor", lambda: fake)

    await desktop_module.async_main(make_args(double_click=[10, 20]))

    assert fake.calls == [("double_click", 10, 20)]
    out = json.loads(capsys.readouterr().out)
    assert out["action"] == "double_click"


@pytest.mark.asyncio
async def test_right_click_routes_through_executor(monkeypatch, desktop_module, capsys):
    fake = FakeExecutor()
    monkeypatch.setattr(desktop_module, "build_executor", lambda: fake)

    await desktop_module.async_main(make_args(right_click=[10, 20]))

    assert fake.calls == [("right_click", 10, 20)]
    out = json.loads(capsys.readouterr().out)
    assert out["action"] == "right_click"


@pytest.mark.asyncio
async def test_move_routes_through_executor(monkeypatch, desktop_module, capsys):
    fake = FakeExecutor()
    monkeypatch.setattr(desktop_module, "build_executor", lambda: fake)

    await desktop_module.async_main(make_args(move=[7, 9]))

    assert fake.calls == [("move", 7, 9)]
    out = json.loads(capsys.readouterr().out)
    assert out["action"] == "move"


@pytest.mark.asyncio
async def test_type_routes_through_executor(monkeypatch, desktop_module, capsys):
    fake = FakeExecutor()
    monkeypatch.setattr(desktop_module, "build_executor", lambda: fake)

    await desktop_module.async_main(make_args(type="hello"))

    assert fake.calls == [("type", "hello")]
    out = json.loads(capsys.readouterr().out)
    assert out["action"] == "type"


@pytest.mark.asyncio
async def test_press_routes_through_executor(monkeypatch, desktop_module, capsys):
    fake = FakeExecutor()
    monkeypatch.setattr(desktop_module, "build_executor", lambda: fake)

    await desktop_module.async_main(make_args(press="enter"))

    assert fake.calls == [("press", "enter")]
    out = json.loads(capsys.readouterr().out)
    assert out["action"] == "press"


@pytest.mark.asyncio
async def test_hotkey_routes_through_executor(monkeypatch, desktop_module, capsys):
    fake = FakeExecutor()
    monkeypatch.setattr(desktop_module, "build_executor", lambda: fake)

    await desktop_module.async_main(make_args(hotkey=["ctrl", "v"]))

    assert fake.calls == [("hotkey", ("ctrl", "v"))]
    out = json.loads(capsys.readouterr().out)
    assert out["action"] == "hotkey"


def test_build_executor_returns_executor_with_input_adapter(desktop_module):
    from core.executor import Executor

    executor = desktop_module.build_executor()

    assert isinstance(executor, Executor)
    assert executor.input_adapter is not None
