import unittest

from aram_helper.hotkeys import GlobalHotkeyService


class FakeKeyboard:
    def __init__(self):
        self.calls = []

    def add_hotkey(self, key, callback):
        self.calls.append((key, callback))
        return f"handle:{key}"

    def remove_hotkey(self, handle):
        self.calls.append(("remove", handle))


class GlobalHotkeyServiceTest(unittest.TestCase):
    def test_registers_scan_hotkey(self):
        keyboard = FakeKeyboard()
        service = GlobalHotkeyService(keyboard_module=keyboard)

        status = service.register("f6", lambda: None)

        self.assertTrue(status.ok)
        self.assertEqual(keyboard.calls[0][0], "f6")

    def test_reports_unavailable_when_keyboard_missing(self):
        service = GlobalHotkeyService(keyboard_module=None)

        status = service.register("f6", lambda: None)

        self.assertFalse(status.ok)
        self.assertIn("不可用", status.message)


if __name__ == "__main__":
    unittest.main()
