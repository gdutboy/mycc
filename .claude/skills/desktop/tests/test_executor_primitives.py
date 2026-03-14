from core.executor import Executor
from core.models import failure_result


MISSING = object()


class FakeRouter:
    def __init__(self):
        self.find_calls = []
        self.read_calls = []
        self.wait_calls = []
        self.find_result = {"ok": True, "action": "find", "target": "发送", "center": [10, 20], "bbox": [0, 0, 20, 40]}
        self.read_result = {"ok": True, "action": "read", "text": "hello"}
        self.wait_result = {"ok": True, "action": "read", "text": "done"}

    def find(self, target, hints=None, region=None, debug=False):
        self.find_calls.append({"target": target, "hints": hints, "region": region, "debug": debug})
        return self.find_result

    def read(self, region=None, hints=None, debug=False):
        self.read_calls.append({"region": region, "hints": hints, "debug": debug})
        return self.read_result

    def wait(self, target=None, mode="find", timeout_ms=1000, interval_ms=100, region=None, hints=None, debug=False):
        self.wait_calls.append(
            {
                "target": target,
                "mode": mode,
                "timeout_ms": timeout_ms,
                "interval_ms": interval_ms,
                "region": region,
                "hints": hints,
                "debug": debug,
            }
        )
        return self.wait_result


class FakeInputAdapter:
    def __init__(self):
        self.calls = []

    def click(self, x=None, y=None, button="left", double=False):
        self.calls.append(("click", x, y, button, double))
        return f"clicked:{button}:{double}"

    def move_to(self, x, y):
        self.calls.append(("move_to", x, y))
        return f"moved:{x}:{y}"

    def scroll(self, clicks):
        self.calls.append(("scroll", clicks))
        return f"scrolled:{clicks}"

    def type_text(self, text):
        self.calls.append(("type_text", text))
        return f"typed:{text}"

    def press_key(self, key):
        self.calls.append(("press_key", key))
        return f"pressed:{key}"

    def hotkey(self, *keys):
        self.calls.append(("hotkey", keys))
        return f"hotkey:{'+'.join(keys)}"


def build_executor(router=None, input_adapter=None):
    router = FakeRouter() if router is None else router
    router = None if router is MISSING else router
    input_adapter = None if input_adapter is MISSING else input_adapter
    return Executor(router=router, input_adapter=input_adapter)


def test_find_delegates_to_router_with_original_arguments():
    router = FakeRouter()
    executor = build_executor(router=router)

    result = executor.find("发送", region=[1, 2, 30, 40], hints={"role": "button"}, debug=True)

    assert result["ok"] is True
    assert result["action"] == "find"
    assert result["target"] == "发送"
    assert router.find_calls == [
        {"target": "发送", "hints": {"role": "button"}, "region": [1, 2, 30, 40], "debug": True}
    ]


def test_find_returns_dependency_unavailable_when_router_missing():
    executor = build_executor(router=MISSING)

    result = executor.find("发送")

    assert result == failure_result("find", "dependency_unavailable", "router is unavailable", {"dependency": "router"})


def test_read_delegates_to_router_with_original_arguments():
    router = FakeRouter()
    executor = build_executor(router=router)

    result = executor.read(region=[3, 4, 50, 60], hints={"backend": "uia"}, debug=True)

    assert result["ok"] is True
    assert result["action"] == "read"
    assert result["text"] == "hello"
    assert router.read_calls == [
        {"region": [3, 4, 50, 60], "hints": {"backend": "uia"}, "debug": True}
    ]


def test_read_returns_dependency_unavailable_when_router_missing():
    executor = build_executor(router=MISSING)

    result = executor.read(region=[3, 4, 50, 60])

    assert result == failure_result("read", "dependency_unavailable", "router is unavailable", {"dependency": "router"})


def test_click_calls_input_adapter_after_safety_check_passes():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.click(10, 20, safety={"level": "yellow"})

    assert result["ok"] is True
    assert result["action"] == "click"
    assert result["point"] == [10, 20]
    assert result["context"] == {
        "safety_level": "yellow",
        "dangerous": False,
        "confirm_required": False,
        "confirmed": False,
    }
    assert adapter.calls == [("click", 10, 20, "left", False)]


def test_double_click_uses_double_flag_on_input_adapter():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.double_click(10, 20)

    assert result["ok"] is True
    assert result["action"] == "double_click"
    assert result["point"] == [10, 20]
    assert adapter.calls == [("click", 10, 20, "left", True)]


def test_right_click_uses_right_button_on_input_adapter():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.right_click(10, 20)

    assert result["ok"] is True
    assert result["action"] == "right_click"
    assert result["point"] == [10, 20]
    assert adapter.calls == [("click", 10, 20, "right", False)]


def test_move_calls_input_adapter_move_to():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.move(7, 9)

    assert result["ok"] is True
    assert result["action"] == "move"
    assert result["point"] == [7, 9]
    assert adapter.calls == [("move_to", 7, 9)]


def test_type_calls_input_adapter_type_text():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.type("hello", safety={"level": "yellow"})

    assert result["ok"] is True
    assert result["action"] == "type"
    assert result["input_length"] == 5
    assert result["context"] == {
        "safety_level": "yellow",
        "dangerous": False,
        "confirm_required": False,
        "confirmed": False,
    }
    assert adapter.calls == [("type_text", "hello")]


def test_press_calls_input_adapter_press_key():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.press("enter", safety={"level": "yellow"})

    assert result["ok"] is True
    assert result["action"] == "press"
    assert result["key"] == "enter"
    assert adapter.calls == [("press_key", "enter")]


def test_hotkey_calls_input_adapter_hotkey():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.hotkey("ctrl", "v", safety={"level": "yellow"})

    assert result["ok"] is True
    assert result["action"] == "hotkey"
    assert result["keys"] == ["ctrl", "v"]
    assert adapter.calls == [("hotkey", ("ctrl", "v"))]


def test_scroll_calls_input_adapter_after_safety_check_passes():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.scroll(-5, safety={"level": "yellow"})

    assert result["ok"] is True
    assert result["action"] == "scroll"
    assert result["clicks"] == -5
    assert result["context"] == {
        "safety_level": "yellow",
        "dangerous": False,
        "confirm_required": False,
        "confirmed": False,
    }
    assert adapter.calls == [("scroll", -5)]


def test_scroll_returns_unsafe_action_without_touching_adapter_when_confirmation_missing():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.scroll(-5, safety={"level": "red", "dangerous": True, "confirm_required": True})

    assert result["ok"] is False
    assert result["action"] == "scroll"
    assert result["reason"] == "unsafe_action"
    assert adapter.calls == []


def test_scroll_returns_dependency_unavailable_when_input_adapter_missing():
    executor = build_executor(input_adapter=None)

    result = executor.scroll(0)

    assert result == failure_result("scroll", "dependency_unavailable", "input_adapter is unavailable", {"dependency": "input_adapter"})


def test_click_returns_unsafe_action_without_touching_adapter_when_confirmation_missing():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.click(10, 20, safety={"level": "red", "dangerous": True, "confirm_required": True})

    assert result["ok"] is False
    assert result["action"] == "click"
    assert result["reason"] == "unsafe_action"
    assert adapter.calls == []


def test_click_allows_confirmed_red_action_and_calls_adapter():
    adapter = FakeInputAdapter()
    executor = build_executor(input_adapter=adapter)

    result = executor.click(
        10,
        20,
        safety={"level": "red", "dangerous": True, "confirm_required": True, "confirmed": True},
    )

    assert result["ok"] is True
    assert result["action"] == "click"
    assert result["context"] == {
        "safety_level": "red",
        "dangerous": True,
        "confirm_required": True,
        "confirmed": True,
    }
    assert adapter.calls == [("click", 10, 20, "left", False)]


def test_click_returns_dependency_unavailable_when_input_adapter_missing():
    executor = build_executor(input_adapter=None)

    result = executor.click(10, 20)

    assert result["ok"] is False
    assert result["action"] == "click"
    assert result["reason"] == "dependency_unavailable"
    assert result["message"]
    assert result["context"] == {"dependency": "input_adapter"}


def test_double_click_returns_dependency_unavailable_when_input_adapter_missing():
    executor = build_executor(input_adapter=None)

    result = executor.double_click(10, 20)

    assert result == failure_result(
        "double_click", "dependency_unavailable", "input_adapter is unavailable", {"dependency": "input_adapter"}
    )


def test_right_click_returns_dependency_unavailable_when_input_adapter_missing():
    executor = build_executor(input_adapter=None)

    result = executor.right_click(10, 20)

    assert result == failure_result(
        "right_click", "dependency_unavailable", "input_adapter is unavailable", {"dependency": "input_adapter"}
    )


def test_move_returns_dependency_unavailable_when_input_adapter_missing():
    executor = build_executor(input_adapter=None)

    result = executor.move(7, 9)

    assert result == failure_result("move", "dependency_unavailable", "input_adapter is unavailable", {"dependency": "input_adapter"})


def test_type_returns_dependency_unavailable_when_input_adapter_missing():
    executor = build_executor(input_adapter=None)

    result = executor.type("hello")

    assert result == failure_result("type", "dependency_unavailable", "input_adapter is unavailable", {"dependency": "input_adapter"})


def test_press_returns_dependency_unavailable_when_input_adapter_missing():
    executor = build_executor(input_adapter=None)

    result = executor.press("enter")

    assert result == failure_result("press", "dependency_unavailable", "input_adapter is unavailable", {"dependency": "input_adapter"})


def test_hotkey_returns_dependency_unavailable_when_input_adapter_missing():
    executor = build_executor(input_adapter=None)

    result = executor.hotkey("ctrl", "v")

    assert result == failure_result("hotkey", "dependency_unavailable", "input_adapter is unavailable", {"dependency": "input_adapter"})


def test_assert_with_find_mode_returns_success_when_target_exists():
    router = FakeRouter()
    executor = build_executor(router=router)

    result = executor.assert_("发送", mode="find", region=[0, 0, 10, 10], hints={"role": "button"}, debug=True)

    assert result == {"ok": True, "action": "assert", "matched": True}
    assert router.find_calls == [
        {"target": "发送", "hints": {"role": "button"}, "region": [0, 0, 10, 10], "debug": True}
    ]


def test_assert_with_read_mode_returns_success_when_text_is_present():
    router = FakeRouter()
    router.read_result = {"ok": True, "action": "read", "text": "hello world"}
    executor = build_executor(router=router)

    result = executor.assert_("hello", mode="read", region=[0, 0, 10, 10])

    assert result == {"ok": True, "action": "assert", "matched": True}
    assert router.read_calls == [{"region": [0, 0, 10, 10], "hints": None, "debug": False}]


def test_assert_returns_dependency_unavailable_when_router_missing():
    executor = build_executor(router=MISSING)

    result = executor.assert_("发送", mode="find")

    assert result == failure_result("assert", "dependency_unavailable", "router is unavailable", {"dependency": "router"})


def test_assert_returns_assertion_failed_when_find_does_not_match():
    router = FakeRouter()
    router.find_result = {"ok": False, "action": "find", "reason": "not_found", "message": "target not found", "context": {}}
    executor = build_executor(router=router)

    result = executor.assert_("发送", mode="find")

    assert result["ok"] is False
    assert result["action"] == "assert"
    assert result["reason"] == "assertion_failed"
    assert result["message"]
    assert result["context"] == {"mode": "find", "target": "发送"}


def test_assert_returns_assertion_failed_when_read_text_does_not_contain_target():
    router = FakeRouter()
    router.read_result = {"ok": True, "action": "read", "text": "world"}
    executor = build_executor(router=router)

    result = executor.assert_("hello", mode="read")

    assert result["ok"] is False
    assert result["action"] == "assert"
    assert result["reason"] == "assertion_failed"
    assert result["message"]
    assert result["context"] == {"mode": "read", "target": "hello"}


def test_assert_returns_assertion_failed_when_read_observation_itself_fails():
    router = FakeRouter()
    router.read_result = failure_result("read", "not_found", "text not found", {"backend_attempts": ["uia", "ocr"]})
    executor = build_executor(router=router)

    result = executor.assert_("hello", mode="read")

    assert result["ok"] is False
    assert result["action"] == "assert"
    assert result["reason"] == "assertion_failed"
    assert result["message"]
    assert result["context"] == {"mode": "read", "target": "hello"}


def test_wait_delegates_to_router_wait_with_original_arguments():
    router = FakeRouter()
    executor = build_executor(router=router)

    result = executor.wait(
        "发送",
        mode="find",
        timeout_ms=300,
        interval_ms=50,
        region=[1, 2, 30, 40],
        hints={"backend": "ocr"},
        debug=True,
    )

    assert result["ok"] is True
    assert result["action"] == "wait"
    assert result["matched"] is True
    assert result["result"] == router.wait_result
    assert router.wait_calls == [
        {
            "target": "发送",
            "mode": "find",
            "timeout_ms": 300,
            "interval_ms": 50,
            "region": [1, 2, 30, 40],
            "hints": {"backend": "ocr"},
            "debug": True,
        }
    ]


def test_wait_returns_dependency_unavailable_when_router_missing():
    executor = build_executor(router=MISSING)

    result = executor.wait("发送", mode="find")

    assert result == failure_result("wait", "dependency_unavailable", "router is unavailable", {"dependency": "router"})


def test_wait_returns_invalid_mode_when_router_rejects_mode():
    router = FakeRouter()
    router.wait_result = failure_result("wait", "invalid_mode", "wait mode is invalid", {"mode": "invalid"})
    executor = build_executor(router=router)

    result = executor.wait("发送", mode="invalid")

    assert result == failure_result("wait", "invalid_mode", "wait mode is invalid", {"mode": "invalid"})
    assert router.wait_calls == [
        {
            "target": "发送",
            "mode": "invalid",
            "timeout_ms": 1000,
            "interval_ms": 100,
            "region": None,
            "hints": None,
            "debug": False,
        }
    ]


def test_wait_returns_invalid_timeout_when_router_rejects_timeout():
    router = FakeRouter()
    router.wait_result = failure_result("wait", "invalid_timeout", "timeout_ms must be positive", {"timeout_ms": 0})
    executor = build_executor(router=router)

    result = executor.wait("发送", timeout_ms=0)

    assert result == failure_result("wait", "invalid_timeout", "timeout_ms must be positive", {"timeout_ms": 0})
    assert router.wait_calls == [
        {
            "target": "发送",
            "mode": "find",
            "timeout_ms": 0,
            "interval_ms": 100,
            "region": None,
            "hints": None,
            "debug": False,
        }
    ]


def test_wait_returns_invalid_interval_when_router_rejects_interval():
    router = FakeRouter()
    router.wait_result = failure_result("wait", "invalid_interval", "interval_ms must be positive", {"interval_ms": 0})
    executor = build_executor(router=router)

    result = executor.wait("发送", interval_ms=0)

    assert result == failure_result("wait", "invalid_interval", "interval_ms must be positive", {"interval_ms": 0})
    assert router.wait_calls == [
        {
            "target": "发送",
            "mode": "find",
            "timeout_ms": 1000,
            "interval_ms": 0,
            "region": None,
            "hints": None,
            "debug": False,
        }
    ]


def test_wait_returns_router_failure_with_unified_wait_action():
    router = FakeRouter()
    router.wait_result = failure_result("read", "timeout", "wait timed out", {"mode": "read", "target": "发送"})
    executor = build_executor(router=router)

    result = executor.wait("发送", mode="read", timeout_ms=300, interval_ms=50)

    assert result == failure_result("wait", "timeout", "wait timed out", {"mode": "read", "target": "发送"})
