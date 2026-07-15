"""WindowsInput - unified Windows input abstraction."""
try:
    import pyautogui
    HAS_UI = True
except ImportError:
    HAS_UI = False

class WindowsInput:
    @staticmethod
    def click(x, y, button="left"):
        if HAS_UI: pyautogui.click(x, y, button=button)

    @staticmethod
    def type_text(text, interval=0.05):
        if HAS_UI: pyautogui.write(text, interval=interval)

    @staticmethod
    def hotkey(*keys):
        if HAS_UI: pyautogui.hotkey(*keys)

    @staticmethod
    def scroll(clicks):
        if HAS_UI: pyautogui.scroll(clicks)

    @staticmethod
    def move_to(x, y, duration=0.3):
        if HAS_UI: pyautogui.moveTo(x, y, duration=duration)

    @staticmethod
    def screenshot():
        if HAS_UI: return pyautogui.screenshot()
        return None
