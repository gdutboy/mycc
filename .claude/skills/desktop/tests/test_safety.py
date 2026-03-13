from core.safety import ensure_action_allowed


def test_confirm_required_blocks_unconfirmed_action():
    result = ensure_action_allowed("click", {"confirm_required": True, "level": "red"})
    assert result["ok"] is False
    assert result["reason"] == "unsafe_action"


def test_confirmed_action_passes_with_context():
    context = ensure_action_allowed(
        "click",
        {"confirm_required": True, "confirmed": True, "dangerous": True, "level": "red"},
    )
    assert context == {
        "safety_level": "red",
        "dangerous": True,
        "confirm_required": True,
        "confirmed": True,
    }


def test_missing_safety_defaults_to_green_context():
    context = ensure_action_allowed("click", None)
    assert context == {
        "safety_level": "green",
        "dangerous": False,
        "confirm_required": False,
        "confirmed": False,
    }
