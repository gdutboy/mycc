from adapters import input as desktop_input


def test_click_passes_coordinates_button_and_double_flag(monkeypatch):
    recorded = []

    def fake_click(*args, **kwargs):
        recorded.append((args, kwargs))

    monkeypatch.setattr(desktop_input.pyautogui, "click", fake_click)

    message = desktop_input.click(10, 20, button="right", double=True)

    assert message == "点击 (10, 20)"
    assert recorded == [((10, 20), {"clicks": 2, "button": "right"})]


def test_click_without_coordinates_clicks_current_position(monkeypatch):
    recorded = []

    def fake_click(*args, **kwargs):
        recorded.append((args, kwargs))

    monkeypatch.setattr(desktop_input.pyautogui, "click", fake_click)

    message = desktop_input.click()

    assert message == "点击当前位置"
    assert recorded == [((), {"clicks": 1, "button": "left"})]


def test_press_key_normalizes_alias_before_press(monkeypatch):
    pressed = []
    monkeypatch.setattr(desktop_input.pyautogui, "press", lambda key: pressed.append(key))

    message = desktop_input.press_key("return")

    assert message == "按下: enter"
    assert pressed == ["enter"]


def test_press_key_passthroughs_unknown_key(monkeypatch):
    pressed = []
    monkeypatch.setattr(desktop_input.pyautogui, "press", lambda key: pressed.append(key))

    message = desktop_input.press_key("f7")

    assert message == "按下: f7"
    assert pressed == ["f7"]


def test_hotkey_delegates_all_keys(monkeypatch):
    recorded = []
    monkeypatch.setattr(desktop_input.pyautogui, "hotkey", lambda *keys: recorded.append(keys))

    message = desktop_input.hotkey("ctrl", "shift", "s")

    assert message == "按下组合键: ctrl+shift+s"
    assert recorded == [("ctrl", "shift", "s")]
