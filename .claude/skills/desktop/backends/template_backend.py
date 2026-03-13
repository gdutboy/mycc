from core.models import failure_result


class TemplateBackend:
    def find(self, target, region=None):
        return failure_result("find", "backend_unavailable", "template backend is not available", {"target": target, "region": region})

    def read(self, region=None):
        return failure_result("read", "backend_unavailable", "template backend is not available", {"region": region})
