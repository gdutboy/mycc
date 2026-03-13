from core.models import failure_result


DEFAULT_SAFETY_CONTEXT = {
    "safety_level": "green",
    "dangerous": False,
    "confirm_required": False,
    "confirmed": False,
}


def ensure_action_allowed(action, safety):
    context = {
        "safety_level": (safety or {}).get("level", "green"),
        "dangerous": bool((safety or {}).get("dangerous", False)),
        "confirm_required": bool((safety or {}).get("confirm_required", False)),
        "confirmed": bool((safety or {}).get("confirmed", False)),
    }

    if context["confirm_required"] and not context["confirmed"]:
        return failure_result(action, "unsafe_action", "action requires confirmation", context)

    return context
