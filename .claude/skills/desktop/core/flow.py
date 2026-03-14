_SUPPORTED_ACTIONS = {
    "click": "click",
    "type": "type",
    "press": "press",
    "wait": "wait",
}


def run_flow(executor, steps):
    results = []

    for index, step in enumerate(steps):
        action = step["action"]
        if action not in _SUPPORTED_ACTIONS:
            return {
                "ok": False,
                "action": "flow",
                "reason": "unsupported_action",
                "step_index": index,
                "step_action": action,
                "steps_total": len(steps),
                "steps_completed": len(results),
                "results": results,
            }
        method_name = _SUPPORTED_ACTIONS[action]
        args = step.get("args", [])
        kwargs = step.get("kwargs", {})

        result = getattr(executor, method_name)(*args, **kwargs)
        results.append(result)

        if not result.get("ok"):
            return {
                "ok": False,
                "action": "flow",
                "reason": "step_failed",
                "step_index": index,
                "step_action": action,
                "steps_total": len(steps),
                "steps_completed": index,
                "results": results,
                "error": result,
            }

    return {
        "ok": True,
        "action": "flow",
        "steps_total": len(steps),
        "steps_completed": len(results),
        "results": results,
    }
