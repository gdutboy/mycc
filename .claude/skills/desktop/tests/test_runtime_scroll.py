from core.runtime import _InputAdapterWrapper


def test_input_adapter_wrapper_scroll_delegates_to_input_module(monkeypatch):
    calls = []

    def fake_scroll(clicks):
        calls.append(clicks)
        return f"scrolled:{clicks}"

    monkeypatch.setattr("core.runtime.input_adapter.scroll", fake_scroll)

    wrapper = _InputAdapterWrapper()
    result = wrapper.scroll(-5)

    assert result == "scrolled:-5"
    assert calls == [-5]
