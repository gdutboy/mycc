from adapters import screen


class FakeImage:
    def __init__(self):
        self.saved_to = None

    def save(self, path):
        self.saved_to = path


def test_capture_screen_uses_mss_monitor_for_region(monkeypatch):
    calls = []
    fake_image = FakeImage()

    class FakeGrabResult:
        size = (30, 40)
        bgra = b"raw-bytes"

    class FakeMSSSession:
        monitors = [{"left": 0, "top": 0, "width": 100, "height": 100}]

        def grab(self, monitor):
            calls.append(monitor)
            return FakeGrabResult()

    monkeypatch.setattr(screen.mss, "mss", lambda: FakeMSSSession())
    monkeypatch.setattr(screen.Image, "frombytes", lambda *args: fake_image)

    result = screen.capture_screen(region=(1, 2, 30, 40))

    assert result is fake_image
    assert calls == [{"left": 1, "top": 2, "width": 30, "height": 40}]


def test_capture_screen_falls_back_to_pyautogui(monkeypatch):
    calls = []
    fake_image = FakeImage()

    class FakeMSSFactory:
        def __call__(self):
            raise RuntimeError("mss unavailable")

    def fake_screenshot(region=None):
        calls.append(region)
        return fake_image

    monkeypatch.setattr(screen, "mss", type("FakeMSSModule", (), {"mss": FakeMSSFactory()})())
    monkeypatch.setattr(screen.pyautogui, "screenshot", fake_screenshot)

    result = screen.capture_screen(region=(1, 2, 30, 40))

    assert result is fake_image
    assert calls == [(1, 2, 30, 40)]


def test_capture_screen_saves_file_when_path_provided(monkeypatch, tmp_path):
    calls = []
    fake_image = FakeImage()

    class FakeMSSFactory:
        def __call__(self):
            raise RuntimeError("mss unavailable")

    def fake_screenshot(region=None):
        calls.append(region)
        return fake_image

    monkeypatch.setattr(screen, "mss", type("FakeMSSModule", (), {"mss": FakeMSSFactory()})())
    monkeypatch.setattr(screen.pyautogui, "screenshot", fake_screenshot)

    output = tmp_path / "screen.png"
    result = screen.capture_screen(save_path=str(output))

    assert result is fake_image
    assert calls == [None]
    assert fake_image.saved_to == str(output)


def test_get_screen_size_delegates_to_pyautogui(monkeypatch):
    monkeypatch.setattr(screen.pyautogui, "size", lambda: (1920, 1080))

    assert screen.get_screen_size() == (1920, 1080)
