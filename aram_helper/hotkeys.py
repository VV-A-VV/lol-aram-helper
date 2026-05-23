from dataclasses import dataclass


_MISSING = object()


@dataclass(frozen=True)
class HotkeyStatus:
    ok: bool
    message: str


class GlobalHotkeyService:
    def __init__(self, keyboard_module=_MISSING):
        if keyboard_module is _MISSING:
            keyboard_module = self._load_keyboard_module()
        self.keyboard = keyboard_module
        self.handle = None

    def register(self, key: str, callback) -> HotkeyStatus:
        if not self.keyboard:
            return HotkeyStatus(False, "全局热键不可用")

        try:
            self.handle = self.keyboard.add_hotkey(key, callback)
            return HotkeyStatus(True, f"全局热键已启用: {key.upper()}")
        except Exception as exc:
            return HotkeyStatus(False, f"全局热键不可用: {exc}")

    def close(self):
        if self.keyboard and self.handle is not None:
            try:
                self.keyboard.remove_hotkey(self.handle)
            except Exception:
                pass
            self.handle = None

    def _load_keyboard_module(self):
        try:
            import keyboard

            return keyboard
        except Exception:
            return None
