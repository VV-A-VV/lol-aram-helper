import unittest

from aram_helper.ocr_service import OcrRegions, parse_rapidocr_result


class OcrServiceTest(unittest.TestCase):
    def test_parse_rapidocr_result_combines_text(self):
        raw = [
            [[[0, 0], [1, 0], [1, 1], [0, 1]], "祖母的", 0.99],
            [[[0, 0], [1, 0], [1, 1], [0, 1]], "辣椒油", 0.98],
        ]

        text = parse_rapidocr_result(raw)

        self.assertEqual(text, "祖母的 辣椒油")

    def test_default_regions_has_three_slots(self):
        regions = OcrRegions.default_2k()

        self.assertEqual(len(regions.slots), 3)
        self.assertEqual(regions.slots[0]["width"], 480)


if __name__ == "__main__":
    unittest.main()
