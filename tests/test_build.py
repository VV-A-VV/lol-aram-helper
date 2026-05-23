from pathlib import Path
import unittest


class BuildScriptTest(unittest.TestCase):
    def test_pyinstaller_collects_rapidocr_package_data(self):
        build_script = Path("build.py").read_text(encoding="utf-8")

        self.assertIn("--collect-all=rapidocr_onnxruntime", build_script)


if __name__ == "__main__":
    unittest.main()
