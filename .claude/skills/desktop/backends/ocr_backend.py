class OCRBackend:
    def __init__(self, screen, ocr):
        self.screen = screen
        self.ocr = ocr

    def find(self, target, region=None):
        image = self.screen.capture_screen(region=region)
        result = self.ocr.recognize(image)
        matches = []
        for line in getattr(result, "lines", []):
            for word in getattr(line, "words", []):
                text = getattr(word, "text", "").strip()
                if text != target:
                    continue
                rect = getattr(word, "bounding_rect", None)
                if rect is None:
                    continue
                bbox = [rect.x, rect.y, rect.width, rect.height]
                matches.append(
                    {
                        "text": text,
                        "backend": "ocr",
                        "bbox": bbox,
                        "center": [rect.x + rect.width // 2, rect.y + rect.height // 2],
                    }
                )
        return matches

    def read(self, region=None):
        image = self.screen.capture_screen(region=region)
        result = self.ocr.recognize(image)
        lines = []
        for line in getattr(result, "lines", []):
            text = getattr(line, "text", "").strip()
            if text:
                lines.append(text)
        return "\n".join(lines)
