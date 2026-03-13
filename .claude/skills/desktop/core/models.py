def success_result(action, **payload):
    return {
        "ok": True,
        "action": action,
        **payload,
    }


def failure_result(action, reason, message, context):
    return {
        "ok": False,
        "action": action,
        "reason": reason,
        "message": message,
        "context": context or {},
    }
