from dataclasses import dataclass


@dataclass(frozen=True)
class OcrRegions:
    slots: tuple[dict[str, int], dict[str, int], dict[str, int]]

    @classmethod
    def default_2k(cls):
        return cls(
            slots=(
                {"top": 810, "left": 975, "width": 480, "height": 90},
                {"top": 810, "left": 1695, "width": 480, "height": 90},
                {"top": 810, "left": 2400, "width": 480, "height": 90},
            )
        )


def parse_rapidocr_result(result) -> str:
    if not result:
        return ""

    texts = []
    for line in result:
        if len(line) < 2:
            continue
        text = line[1]
        if isinstance(text, (tuple, list)) and text:
            text = text[0]
        if text:
            texts.append(str(text).strip())
    return " ".join(texts).strip()


class HextechOcrService:
    def __init__(self, regions: OcrRegions | None = None):
        import cv2
        import mss
        import numpy as np
        from rapidocr_onnxruntime import RapidOCR

        self.cv2 = cv2
        self.mss = mss
        self.np = np
        self.ocr = RapidOCR()
        self.screen = mss.mss()
        self.regions = regions or OcrRegions.default_2k()

    def recognize_augments(self) -> tuple[str, str, str]:
        return tuple(self._recognize_region(region) for region in self.regions.slots)

    def _recognize_region(self, region: dict[str, int]) -> str:
        screenshot = self.screen.grab(region)
        image = self.np.array(screenshot)
        image = self.cv2.cvtColor(image, self.cv2.COLOR_BGRA2BGR)
        result, _ = self.ocr(image)
        return parse_rapidocr_result(result)
