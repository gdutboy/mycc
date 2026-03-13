from core.router import Router


class FakeOCRBackend:
    def __init__(self, read_text="", calls=None):
        self.read_text = read_text
        self.calls = calls if calls is not None else []

    def read(self, region=None):
        self.calls.append(("read", region))
        return self.read_text


class FakeUIABackend:
    def __init__(self, read_text="", calls=None):
        self.read_text = read_text
        self.calls = calls if calls is not None else []

    def read(self, region=None):
        self.calls.append(("read", region))
        return self.read_text


def build_router(ocr=None, uia=None, sleep_func=None):
    return Router(
        ocr_backend=ocr,
        uia_backend=uia,
        template_backend=None,
        sleep_func=sleep_func or (lambda _seconds: None),
    )


def test_read_prefers_uia_for_visible_text_controls():
    uia = FakeUIABackend(read_text="hello")
    ocr = FakeOCRBackend(read_text="ocr hello")
    router = build_router(ocr=ocr, uia=uia)

    result = router.read(region=[0, 0, 100, 100])

    assert result["ok"] is True
    assert result["action"] == "read"
    assert result["backend"] == "uia"
    assert result["text"] == "hello"
    assert result["context"]["backend_attempts"] == ["uia"]
    assert uia.calls == [("read", [0, 0, 100, 100])]
    assert ocr.calls == []


def test_read_falls_back_to_ocr_when_uia_returns_empty_text():
    uia = FakeUIABackend(read_text="")
    ocr = FakeOCRBackend(read_text="ocr hello")
    router = build_router(ocr=ocr, uia=uia)

    result = router.read(region=[0, 0, 100, 100])

    assert result["ok"] is True
    assert result["backend"] == "ocr"
    assert result["text"] == "ocr hello"
    assert result["context"]["backend_attempts"] == ["uia", "ocr"]
    assert uia.calls == [("read", [0, 0, 100, 100])]
    assert ocr.calls == [("read", [0, 0, 100, 100])]


def test_read_returns_backend_unavailable_when_explicit_backend_missing():
    router = build_router(ocr=FakeOCRBackend(read_text="hello"), uia=None)

    result = router.read(region=[0, 0, 100, 100], hints={"backend": "uia"})

    assert result["ok"] is False
    assert result["action"] == "read"
    assert result["reason"] == "backend_unavailable"
    assert result["context"] == {"backend": "uia"}


def test_read_uses_only_explicit_backend_without_fallback():
    uia = FakeUIABackend(read_text="")
    ocr = FakeOCRBackend(read_text="ocr hello")
    router = build_router(ocr=ocr, uia=uia)

    result = router.read(region=[0, 0, 100, 100], hints={"backend": "uia"})

    assert result["ok"] is False
    assert result["action"] == "read"
    assert result["reason"] == "not_found"
    assert result["context"]["backend_attempts"] == ["uia"]
    assert uia.calls == [("read", [0, 0, 100, 100])]
    assert ocr.calls == []


def test_wait_poll_read_until_text_is_available():
    calls = []

    class PollingRouter(Router):
        def __init__(self):
            super().__init__(ocr_backend=None, uia_backend=None, template_backend=None, sleep_func=lambda seconds: calls.append(seconds))
            self.attempt = 0

        def read(self, region=None, hints=None, debug=False):
            self.attempt += 1
            if self.attempt < 2:
                return {"ok": False, "action": "read", "reason": "not_found", "message": "text not found", "context": {"backend_attempts": ["uia"]}}
            return {"ok": True, "action": "read", "backend": "uia", "text": "hello", "context": {"backend_attempts": ["uia"]}}

    router = PollingRouter()

    result = router.wait(mode="read", timeout_ms=120, interval_ms=30, region=[0, 0, 100, 100])

    assert result["ok"] is True
    assert result["action"] == "read"
    assert result["text"] == "hello"
    assert calls == [0.03]


def test_wait_read_passes_region_through_to_read():
    calls = []

    class RegionRouter(Router):
        def __init__(self):
            super().__init__(ocr_backend=None, uia_backend=None, template_backend=None, sleep_func=lambda seconds: calls.append(seconds))
            self.regions = []

        def read(self, region=None, hints=None, debug=False):
            self.regions.append(region)
            return {"ok": True, "action": "read", "backend": "uia", "text": "hello", "context": {"backend_attempts": ["uia"]}}

    router = RegionRouter()

    result = router.wait(mode="read", timeout_ms=120, interval_ms=30, region=[1, 2, 3, 4])

    assert result["ok"] is True
    assert result["text"] == "hello"
    assert router.regions == [[1, 2, 3, 4]]
    assert calls == []


def test_wait_rejects_non_positive_timeout_ms():
    router = build_router()

    result = router.wait("发送", mode="find", timeout_ms=0, interval_ms=40)

    assert result["ok"] is False
    assert result["action"] == "wait"
    assert result["reason"] == "invalid_timeout"
    assert result["context"] == {"timeout_ms": 0}


def test_wait_rejects_non_positive_interval_ms():
    router = build_router()

    result = router.wait("发送", mode="find", timeout_ms=120, interval_ms=0)

    assert result["ok"] is False
    assert result["action"] == "wait"
    assert result["reason"] == "invalid_interval"
    assert result["context"] == {"interval_ms": 0}
