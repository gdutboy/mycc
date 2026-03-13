from core.models import success_result
from core.router import Router


class FakeOCRBackend:
    def __init__(self, matches=None, read_text="", calls=None):
        self.matches = list(matches or [])
        self.read_text = read_text
        self.calls = calls if calls is not None else []

    def find(self, target, region=None):
        self.calls.append(("find", target, region))
        return list(self.matches)

    def read(self, region=None):
        self.calls.append(("read", region))
        return self.read_text


class FakeUIABackend:
    def __init__(self, matches=None, read_text="", calls=None):
        self.matches = list(matches or [])
        self.read_text = read_text
        self.calls = calls if calls is not None else []

    def find(self, target, hints=None, region=None):
        self.calls.append(("find", target, hints, region))
        return list(self.matches)

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


def test_find_prefers_ocr_for_plain_text_targets():
    ocr = FakeOCRBackend(matches=[{"text": "发送", "backend": "ocr", "bbox": [0, 0, 80, 36], "center": [40, 18]}])
    uia = FakeUIABackend(matches=[{"text": "发送", "role": "Button", "backend": "uia", "bbox": [1, 1, 90, 40], "center": [46, 21]}])
    router = build_router(ocr=ocr, uia=uia)

    result = router.find("发送")

    assert result["ok"] is True
    assert result["action"] == "find"
    assert result["backend"] == "ocr"
    assert result["bbox"] == [0, 0, 80, 36]
    assert result["center"] == [40, 18]
    assert result["context"]["backend_attempts"] == ["ocr"]
    assert ocr.calls == [("find", "发送", None)]
    assert uia.calls == []


def test_find_prefers_uia_when_role_hint_is_present():
    ocr = FakeOCRBackend(matches=[{"text": "发送", "backend": "ocr", "bbox": [0, 0, 80, 36], "center": [40, 18]}])
    uia = FakeUIABackend(matches=[{"text": "发送", "role": "Button", "backend": "uia", "bbox": [10, 10, 60, 24], "center": [40, 22]}])
    router = build_router(ocr=ocr, uia=uia)

    result = router.find("发送", hints={"role": "button"}, region=[0, 0, 100, 100])

    assert result["ok"] is True
    assert result["backend"] == "uia"
    assert result["context"]["backend_attempts"] == ["uia"]
    assert uia.calls == [("find", "发送", {"role": "button"}, [0, 0, 100, 100])]
    assert ocr.calls == []


def test_find_returns_backend_unavailable_for_missing_explicit_backend():
    router = build_router(ocr=FakeOCRBackend(), uia=None)

    result = router.find("发送", hints={"backend": "uia"})

    assert result["ok"] is False
    assert result["action"] == "find"
    assert result["reason"] == "backend_unavailable"
    assert result["context"] == {"backend": "uia"}


def test_find_uses_only_explicit_backend_without_fallback():
    ocr = FakeOCRBackend(matches=[])
    uia = FakeUIABackend(matches=[{"text": "发送", "role": "Button", "backend": "uia", "bbox": [10, 10, 60, 24], "center": [40, 22]}])
    router = build_router(ocr=ocr, uia=uia)

    result = router.find("发送", hints={"backend": "ocr"}, region=[0, 0, 100, 100])

    assert result["ok"] is False
    assert result["action"] == "find"
    assert result["reason"] == "not_found"
    assert result["context"]["backend_attempts"] == ["ocr"]
    assert ocr.calls == [("find", "发送", [0, 0, 100, 100])]
    assert uia.calls == []


def test_find_returns_not_found_when_all_backends_miss():
    ocr = FakeOCRBackend(matches=[])
    uia = FakeUIABackend(matches=[])
    router = build_router(ocr=ocr, uia=uia)

    result = router.find("发送")

    assert result["ok"] is False
    assert result["action"] == "find"
    assert result["reason"] == "not_found"
    assert result["context"]["backend_attempts"] == ["ocr", "uia"]


def test_wait_poll_find_until_match_is_available():
    calls = []

    class PollingRouter(Router):
        def __init__(self):
            super().__init__(ocr_backend=None, uia_backend=None, template_backend=None, sleep_func=lambda seconds: calls.append(seconds))
            self.attempt = 0

        def find(self, target, hints=None, region=None, debug=False):
            self.attempt += 1
            if self.attempt < 3:
                return {"ok": False, "action": "find", "reason": "not_found", "message": "target not found", "context": {"backend_attempts": ["ocr"]}}
            return success_result("find", backend="ocr", target=target, bbox=[1, 2, 3, 4], center=[2, 4], context={"backend_attempts": ["ocr"]})

    router = PollingRouter()

    result = router.wait("发送", mode="find", timeout_ms=300, interval_ms=50)

    assert result["ok"] is True
    assert result["action"] == "find"
    assert result["target"] == "发送"
    assert calls == [0.05, 0.05]


def test_wait_returns_timeout_when_find_never_succeeds():
    calls = []

    class TimeoutRouter(Router):
        def __init__(self):
            super().__init__(ocr_backend=None, uia_backend=None, template_backend=None, sleep_func=lambda seconds: calls.append(seconds))

        def find(self, target, hints=None, region=None, debug=False):
            return {"ok": False, "action": "find", "reason": "not_found", "message": "target not found", "context": {"backend_attempts": ["ocr"]}}

    router = TimeoutRouter()

    result = router.wait("发送", mode="find", timeout_ms=120, interval_ms=40)

    assert result["ok"] is False
    assert result["action"] == "wait"
    assert result["reason"] == "timeout"
    assert result["context"]["mode"] == "find"
    assert result["context"]["target"] == "发送"
    assert calls == [0.04, 0.04, 0.04]


def test_wait_rejects_unknown_mode():
    router = build_router()

    result = router.wait("发送", mode="watch")

    assert result["ok"] is False
    assert result["action"] == "wait"
    assert result["reason"] == "invalid_mode"
    assert result["context"] == {"mode": "watch"}
