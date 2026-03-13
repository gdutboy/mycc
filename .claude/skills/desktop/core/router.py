from core.models import failure_result, success_result


class Router:
    def __init__(self, ocr_backend=None, uia_backend=None, template_backend=None, sleep_func=None):
        self.ocr_backend = ocr_backend
        self.uia_backend = uia_backend
        self.template_backend = template_backend
        self.sleep_func = sleep_func or (lambda _seconds: None)

    def find(self, target, hints=None, region=None, debug=False):
        hints = hints or {}
        backend_attempts = []
        requested_backend = hints.get("backend")

        for backend_name in self._find_backend_order(hints):
            if requested_backend and backend_name != requested_backend:
                continue

            backend = self._get_backend(backend_name)
            if backend is None:
                if requested_backend:
                    return failure_result("find", "backend_unavailable", f"backend '{backend_name}' unavailable", {"backend": backend_name})
                continue

            backend_attempts.append(backend_name)
            matches = self._call_find(backend_name, backend, target, hints, region)
            if matches:
                match = matches[0]
                return success_result(
                    "find",
                    backend=backend_name,
                    target=target,
                    bbox=match.get("bbox"),
                    center=match.get("center"),
                    context={"backend_attempts": backend_attempts},
                )

        return failure_result("find", "not_found", "target not found", {"backend_attempts": backend_attempts})

    def read(self, region=None, hints=None, debug=False):
        hints = hints or {}
        backend_attempts = []
        requested_backend = hints.get("backend")

        for backend_name in self._read_backend_order(hints):
            if requested_backend and backend_name != requested_backend:
                continue

            backend = self._get_backend(backend_name)
            if backend is None:
                if requested_backend:
                    return failure_result("read", "backend_unavailable", f"backend '{backend_name}' unavailable", {"backend": backend_name})
                continue

            backend_attempts.append(backend_name)
            text = backend.read(region=region)
            if text:
                return success_result(
                    "read",
                    backend=backend_name,
                    text=text,
                    context={"backend_attempts": backend_attempts},
                )
            if requested_backend:
                return failure_result("read", "not_found", "text not found", {"backend_attempts": backend_attempts})

        return failure_result("read", "not_found", "text not found", {"backend_attempts": backend_attempts})

    def wait(self, target=None, mode="find", timeout_ms=1000, interval_ms=100, region=None, hints=None, debug=False):
        if mode not in {"find", "read"}:
            return failure_result("wait", "invalid_mode", "wait mode is invalid", {"mode": mode})
        if timeout_ms <= 0:
            return failure_result("wait", "invalid_timeout", "timeout_ms must be positive", {"timeout_ms": timeout_ms})
        if interval_ms <= 0:
            return failure_result("wait", "invalid_interval", "interval_ms must be positive", {"interval_ms": interval_ms})

        elapsed_ms = 0
        interval_seconds = interval_ms / 1000

        while True:
            if mode == "find":
                result = self.find(target, hints=hints, region=region, debug=debug)
            else:
                result = self.read(region=region, hints=hints, debug=debug)

            if result.get("ok"):
                return result

            if elapsed_ms >= timeout_ms:
                return failure_result("wait", "timeout", "wait timed out", {"mode": mode, "target": target})

            self.sleep_func(interval_seconds)
            elapsed_ms += interval_ms

    def _find_backend_order(self, hints):
        if hints.get("backend"):
            return [hints["backend"]]
        if hints.get("role"):
            return ["uia", "ocr"]
        return ["ocr", "uia"]

    def _read_backend_order(self, hints):
        if hints.get("backend"):
            return [hints["backend"]]
        return ["uia", "ocr"]

    def _get_backend(self, backend_name):
        if backend_name == "ocr":
            return self.ocr_backend
        if backend_name == "uia":
            return self.uia_backend
        if backend_name == "template":
            return self.template_backend
        return None

    def _call_find(self, backend_name, backend, target, hints, region):
        if backend_name == "uia":
            return backend.find(target, hints=hints, region=region)
        return backend.find(target, region=region)
