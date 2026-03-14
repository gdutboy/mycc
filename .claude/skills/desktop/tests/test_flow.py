class FakeExecutor:
    def __init__(self):
        self.calls = []

    def click(self, *args, **kwargs):
        self.calls.append(("click", args, kwargs))
        return {"ok": True, "action": "click", "point": list(args)}

    def type(self, *args, **kwargs):
        self.calls.append(("type", args, kwargs))
        return {"ok": True, "action": "type", "input_length": len(args[0])}

    def press(self, *args, **kwargs):
        self.calls.append(("press", args, kwargs))
        return {"ok": True, "action": "press", "key": args[0]}

    def wait(self, *args, **kwargs):
        self.calls.append(("wait", args, kwargs))
        return {"ok": True, "action": "wait", "matched": True}


def test_run_flow_executes_supported_steps_in_order():
    from core.flow import run_flow

    executor = FakeExecutor()
    steps = [
        {"action": "click", "args": [100, 200]},
        {"action": "type", "args": ["hello"]},
        {"action": "press", "args": ["enter"]},
        {"action": "wait", "kwargs": {"target": "发送", "mode": "find"}},
    ]

    result = run_flow(executor, steps)

    assert result["ok"] is True
    assert result["action"] == "flow"
    assert result["steps_total"] == 4
    assert result["steps_completed"] == 4
    assert [item["action"] for item in result["results"]] == [
        "click",
        "type",
        "press",
        "wait",
    ]
    assert executor.calls == [
        ("click", (100, 200), {}),
        ("type", ("hello",), {}),
        ("press", ("enter",), {}),
        ("wait", (), {"target": "发送", "mode": "find"}),
    ]


def test_run_flow_stops_on_failed_step_and_returns_error_payload():
    from core.flow import run_flow

    class FailOnPressExecutor(FakeExecutor):
        def press(self, *args, **kwargs):
            self.calls.append(("press", args, kwargs))
            return {"ok": False, "action": "press", "reason": "unsafe_action", "message": "blocked"}

    executor = FailOnPressExecutor()
    steps = [
        {"action": "click", "args": [10, 20]},
        {"action": "press", "args": ["enter"]},
        {"action": "type", "args": ["never"]},
    ]

    result = run_flow(executor, steps)

    assert result == {
        "ok": False,
        "action": "flow",
        "reason": "step_failed",
        "step_index": 1,
        "step_action": "press",
        "steps_total": 3,
        "steps_completed": 1,
        "results": [
            {"ok": True, "action": "click", "point": [10, 20]},
            {"ok": False, "action": "press", "reason": "unsafe_action", "message": "blocked"},
        ],
        "error": {"ok": False, "action": "press", "reason": "unsafe_action", "message": "blocked"},
    }
    assert executor.calls == [
        ("click", (10, 20), {}),
        ("press", ("enter",), {}),
    ]


def test_run_flow_returns_unsupported_action_without_calling_executor():
    from core.flow import run_flow

    executor = FakeExecutor()
    steps = [
        {"action": "click", "args": [1, 2]},
        {"action": "scroll", "args": [-5]},
        {"action": "press", "args": ["enter"]},
    ]

    result = run_flow(executor, steps)

    assert result == {
        "ok": False,
        "action": "flow",
        "reason": "unsupported_action",
        "step_index": 1,
        "step_action": "scroll",
        "steps_total": 3,
        "steps_completed": 1,
        "results": [
            {"ok": True, "action": "click", "point": [1, 2]},
        ],
    }
    assert executor.calls == [
        ("click", (1, 2), {}),
    ]
