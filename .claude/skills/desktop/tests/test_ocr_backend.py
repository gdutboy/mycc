from backends.ocr_backend import OCRBackend
from backends.template_backend import TemplateBackend


class FakeScreen:
    def __init__(self, image="fake-image"):
        self.image = image
        self.calls = []

    def capture_screen(self, region=None):
        self.calls.append(region)
        return self.image


class FakeWord:
    def __init__(self, text, bounding_rect):
        self.text = text
        self.bounding_rect = bounding_rect


class FakeRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class FakeLine:
    def __init__(self, text, words):
        self.text = text
        self.words = words


class FakeOCRResult:
    def __init__(self, lines):
        self.lines = lines


class FakeOCR:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def recognize(self, image):
        self.calls.append(image)
        return self.result


def test_ocr_find_returns_normalized_matches():
    result = FakeOCRResult(
        [
            FakeLine(
                text="发送",
                words=[FakeWord("发送", FakeRect(40, 10, 20, 20))],
            )
        ]
    )
    screen = FakeScreen()
    ocr = FakeOCR(result)
    backend = OCRBackend(screen=screen, ocr=ocr)

    matches = backend.find("发送", region=[0, 0, 100, 100])

    assert len(matches) == 1
    assert matches[0]["text"] == "发送"
    assert matches[0]["backend"] == "ocr"
    assert matches[0]["bbox"] == [40, 10, 20, 20]
    assert matches[0]["center"] == [50, 20]
    assert screen.calls == [[0, 0, 100, 100]]
    assert ocr.calls == ["fake-image"]



def test_ocr_read_joins_non_empty_line_texts():
    result = FakeOCRResult(
        [
            FakeLine(text="  第一行  ", words=[]),
            FakeLine(text="", words=[]),
            FakeLine(text="第二行", words=[]),
        ]
    )
    backend = OCRBackend(screen=FakeScreen(), ocr=FakeOCR(result))

    text = backend.read(region=[0, 0, 200, 100])

    assert text == "第一行\n第二行"



def test_ocr_find_returns_empty_list_when_target_missing():
    result = FakeOCRResult([FakeLine(text="取消", words=[FakeWord("取消", FakeRect(0, 0, 10, 10))])])
    backend = OCRBackend(screen=FakeScreen(), ocr=FakeOCR(result))

    matches = backend.find("发送")

    assert matches == []



def test_ocr_read_returns_empty_string_when_no_lines():
    backend = OCRBackend(screen=FakeScreen(), ocr=FakeOCR(FakeOCRResult([])))

    text = backend.read(region=[0, 0, 200, 100])

    assert text == ""



def test_template_backend_find_reports_unavailable():
    backend = TemplateBackend()

    result = backend.find("图标")

    assert result["ok"] is False
    assert result["action"] == "find"
    assert result["reason"] == "backend_unavailable"



def test_template_backend_read_reports_unavailable():
    backend = TemplateBackend()

    result = backend.read(region=[0, 0, 100, 100])

    assert result["ok"] is False
    assert result["action"] == "read"
    assert result["reason"] == "backend_unavailable"
