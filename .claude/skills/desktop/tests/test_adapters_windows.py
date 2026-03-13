import json

from adapters import windows


class FakeWindow:
    def __init__(self, title, box, active=False, hwnd=100):
        self.title = title
        self.box = box
        self.isActive = active
        self._hWnd = hwnd
        self.width = box[2]
        self.height = box[3]


def test_list_windows_serializes_only_titled_windows(monkeypatch):
    fake_windows = [
        FakeWindow("微信", (1, 2, 300, 400), active=True),
        FakeWindow("", (0, 0, 10, 10), active=False),
    ]
    monkeypatch.setattr(windows.gw, "getAllWindows", lambda: fake_windows)

    payload = json.loads(windows.list_windows())

    assert payload == [{"title": "微信", "position": [1, 2, 300, 400], "active": True}]


def test_get_active_window_serializes_current_window(monkeypatch):
    monkeypatch.setattr(windows.gw, "getActiveWindow", lambda: FakeWindow("微信", (1, 2, 300, 400)))

    payload = json.loads(windows.get_active_window())

    assert payload == {"title": "微信", "position": [1, 2, 300, 400], "size": [300, 400]}


def test_activate_window_returns_not_found_when_no_title_matches(monkeypatch):
    monkeypatch.setattr(windows.gw, "getAllWindows", lambda: [FakeWindow("微信", (1, 2, 300, 400))])

    assert windows.activate_window("QQ") == "未找到窗口: QQ"


def test_activate_window_restores_and_foregrounds_matching_window(monkeypatch):
    user32_calls = []

    class FakeUser32:
        def ShowWindow(self, hwnd, mode):
            user32_calls.append(("show", hwnd, mode))

        def SetForegroundWindow(self, hwnd):
            user32_calls.append(("foreground", hwnd))

    monkeypatch.setattr(windows, "get_user32", lambda: FakeUser32())
    monkeypatch.setattr(windows.gw, "getAllWindows", lambda: [FakeWindow("QQ 音乐", (1, 2, 300, 400), hwnd=321)])
    monkeypatch.setattr(windows.time, "sleep", lambda _: None)

    message = windows.activate_window("qq")

    assert message == "已激活窗口: QQ 音乐"
    assert user32_calls == [("show", 321, 9), ("foreground", 321)]
