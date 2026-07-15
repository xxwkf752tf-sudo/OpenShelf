"""ThemeManager - theme switching."""
from pathlib import Path

class ThemeManager:
    _instance = None
    THEMES = {"dark": "resources/themes/dark.qss", "light": "resources/themes/light.qss"}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current = "dark"
            cls._instance._qss_cache = {}
        return cls._instance

    def load_theme(self, theme_name):
        if theme_name in self._qss_cache:
            return self._qss_cache[theme_name]
        theme_file = self.THEMES.get(theme_name)
        if theme_file is None:
            return ""
        p = Path(__file__).parent.parent.parent / theme_file
        if p.exists():
            qss = p.read_text(encoding="utf-8")
            self._qss_cache[theme_name] = qss
            self._current = theme_name
            return qss
        return ""

    def toggle(self):
        n = "light" if self._current == "dark" else "dark"
        return n, self.load_theme(n)
