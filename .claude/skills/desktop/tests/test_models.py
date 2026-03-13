from core.models import failure_result, success_result


def test_success_result_keeps_minimum_schema():
    result = success_result("find", target="发送", center=[1, 2], bbox=[0, 0, 2, 2])
    assert result["ok"] is True
    assert result["action"] == "find"
    assert result["target"] == "发送"
    assert "matches" not in result


def test_failure_result_always_includes_context():
    result = failure_result("find", "not_found", "target text not found", {})
    assert result == {
        "ok": False,
        "action": "find",
        "reason": "not_found",
        "message": "target text not found",
        "context": {},
    }


def test_failure_result_normalizes_none_context():
    result = failure_result("find", "not_found", "target text not found", None)
    assert result["context"] == {}
