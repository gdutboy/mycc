class UIABackend:
    def __init__(self, tree):
        self.tree = tree

    def find(self, target, hints=None, region=None):
        hints = hints or {}
        role_hint = hints.get("role")
        matches = []
        for node in self.tree.read_visible_nodes(region=region):
            if not node.get("is_visible"):
                continue
            role = node.get("role", "")
            if role_hint and role.lower() != str(role_hint).lower():
                continue
            text = (node.get("name") or node.get("value") or "").strip()
            if text != target:
                continue
            bbox = list(node.get("bounds") or [])
            if len(bbox) != 4:
                continue
            x, y, width, height = bbox
            matches.append(
                {
                    "role": role,
                    "text": text,
                    "backend": "uia",
                    "bbox": bbox,
                    "center": [x + width // 2, y + height // 2],
                }
            )
        return matches

    def read(self, region=None):
        lines = []
        for node in self.tree.read_visible_nodes(region=region):
            if not node.get("is_visible"):
                continue
            text = (node.get("name") or node.get("value") or "").strip()
            if text:
                lines.append(text)
        return "\n".join(lines)
