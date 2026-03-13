from backends.uia_backend import UIABackend


class FakeTree:
    def __init__(self, nodes):
        self.nodes = nodes
        self.calls = []

    def read_visible_nodes(self, region=None):
        self.calls.append(region)
        return list(self.nodes)



def test_uia_read_prefers_visible_text_like_controls():
    tree = FakeTree(
        [
            {"role": "Edit", "name": "hello", "value": "", "is_visible": True, "bounds": [0, 0, 10, 10]},
            {"role": "Text", "name": "", "value": "world", "is_visible": True, "bounds": [10, 0, 10, 10]},
            {"role": "Button", "name": "发送", "value": "", "is_visible": False, "bounds": [20, 0, 10, 10]},
        ]
    )
    backend = UIABackend(tree=tree)

    text = backend.read(region=[0, 0, 100, 100])

    assert text == "hello\nworld"
    assert tree.calls == [[0, 0, 100, 100]]



def test_uia_find_can_filter_by_role_hint():
    tree = FakeTree(
        [
            {"role": "Button", "name": "发送", "value": "", "is_visible": True, "bounds": [10, 10, 80, 30]},
            {"role": "Text", "name": "发送", "value": "", "is_visible": True, "bounds": [0, 0, 20, 10]},
        ]
    )
    backend = UIABackend(tree=tree)

    matches = backend.find("发送", hints={"role": "button"}, region=[0, 0, 100, 100])

    assert len(matches) == 1
    assert matches[0]["role"] == "Button"
    assert matches[0]["text"] == "发送"
    assert matches[0]["backend"] == "uia"
    assert matches[0]["bbox"] == [10, 10, 80, 30]
    assert matches[0]["center"] == [50, 25]



def test_uia_find_returns_empty_list_when_no_visible_match():
    tree = FakeTree(
        [
            {"role": "Button", "name": "发送", "value": "", "is_visible": False, "bounds": [10, 10, 80, 30]},
        ]
    )
    backend = UIABackend(tree=tree)

    matches = backend.find("发送")

    assert matches == []



def test_uia_read_returns_empty_string_when_tree_has_no_nodes():
    backend = UIABackend(tree=FakeTree([]))

    text = backend.read(region=[0, 0, 100, 100])

    assert text == ""
