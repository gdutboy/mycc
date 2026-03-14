from core.models import failure_result, success_result
from core.safety import ensure_action_allowed

_ROUTER_UNAVAILABLE = lambda action: failure_result(
    action, "dependency_unavailable", "router is unavailable", {"dependency": "router"}
)
_INPUT_UNAVAILABLE = lambda action: failure_result(
    action, "dependency_unavailable", "input_adapter is unavailable", {"dependency": "input_adapter"}
)


class Executor:
    def __init__(self, router=None, input_adapter=None):
        self.router = router
        self.input_adapter = input_adapter

    # --- observation ---

    def find(self, target, region=None, hints=None, debug=False):
        if self.router is None:
            return _ROUTER_UNAVAILABLE("find")
        return self.router.find(target, hints=hints, region=region, debug=debug)

    def read(self, region=None, hints=None, debug=False):
        if self.router is None:
            return _ROUTER_UNAVAILABLE("read")
        return self.router.read(region=region, hints=hints, debug=debug)

    # --- input ---

    def click(self, x, y, safety=None):
        if self.input_adapter is None:
            return _INPUT_UNAVAILABLE("click")
        safety_result = ensure_action_allowed("click", safety)
        if isinstance(safety_result, dict) and not safety_result.get("ok", True):
            return safety_result
        self.input_adapter.click(x, y, "left", False)
        return success_result("click", point=[x, y], context=safety_result)

    def double_click(self, x, y, safety=None):
        if self.input_adapter is None:
            return _INPUT_UNAVAILABLE("double_click")
        safety_result = ensure_action_allowed("double_click", safety)
        if isinstance(safety_result, dict) and not safety_result.get("ok", True):
            return safety_result
        self.input_adapter.click(x, y, "left", True)
        return success_result("double_click", point=[x, y])

    def right_click(self, x, y, safety=None):
        if self.input_adapter is None:
            return _INPUT_UNAVAILABLE("right_click")
        safety_result = ensure_action_allowed("right_click", safety)
        if isinstance(safety_result, dict) and not safety_result.get("ok", True):
            return safety_result
        self.input_adapter.click(x, y, "right", False)
        return success_result("right_click", point=[x, y])

    def move(self, x, y):
        if self.input_adapter is None:
            return _INPUT_UNAVAILABLE("move")
        self.input_adapter.move_to(x, y)
        return success_result("move", point=[x, y])

    def scroll(self, clicks, safety=None):
        if self.input_adapter is None:
            return _INPUT_UNAVAILABLE("scroll")
        safety_result = ensure_action_allowed("scroll", safety)
        if isinstance(safety_result, dict) and not safety_result.get("ok", True):
            return safety_result
        self.input_adapter.scroll(clicks)
        return success_result("scroll", clicks=clicks, context=safety_result)

    def type(self, text, safety=None):
        if self.input_adapter is None:
            return _INPUT_UNAVAILABLE("type")
        safety_result = ensure_action_allowed("type", safety)
        if isinstance(safety_result, dict) and not safety_result.get("ok", True):
            return safety_result
        self.input_adapter.type_text(text)
        return success_result("type", input_length=len(text), context=safety_result)

    def press(self, key, safety=None):
        if self.input_adapter is None:
            return _INPUT_UNAVAILABLE("press")
        safety_result = ensure_action_allowed("press", safety)
        if isinstance(safety_result, dict) and not safety_result.get("ok", True):
            return safety_result
        self.input_adapter.press_key(key)
        return success_result("press", key=key)

    def hotkey(self, *keys, safety=None):
        if self.input_adapter is None:
            return _INPUT_UNAVAILABLE("hotkey")
        safety_result = ensure_action_allowed("hotkey", safety)
        if isinstance(safety_result, dict) and not safety_result.get("ok", True):
            return safety_result
        self.input_adapter.hotkey(*keys)
        return success_result("hotkey", keys=list(keys))

    # --- assertion ---

    def assert_(self, target, mode="find", region=None, hints=None, debug=False):
        if self.router is None:
            return _ROUTER_UNAVAILABLE("assert")

        if mode == "find":
            result = self.router.find(target, hints=hints, region=region, debug=debug)
            if result.get("ok"):
                return {"ok": True, "action": "assert", "matched": True}
        else:
            result = self.router.read(region=region, hints=hints, debug=debug)
            if result.get("ok") and target in result.get("text", ""):
                return {"ok": True, "action": "assert", "matched": True}

        return failure_result("assert", "assertion_failed", f"assertion failed for target '{target}'", {"mode": mode, "target": target})

    # --- wait ---

    def wait(self, target=None, mode="find", timeout_ms=1000, interval_ms=100, region=None, hints=None, debug=False):
        if self.router is None:
            return _ROUTER_UNAVAILABLE("wait")

        result = self.router.wait(
            target=target,
            mode=mode,
            timeout_ms=timeout_ms,
            interval_ms=interval_ms,
            region=region,
            hints=hints,
            debug=debug,
        )

        if not result.get("ok"):
            return {**result, "action": "wait"}

        return {"ok": True, "action": "wait", "matched": True, "result": result}
