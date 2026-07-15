"""ComputerUseAgent - local Windows desktop automation."""
try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

class ComputerUseAgent:
    SAFETY_TIMEOUT = 30

    def __init__(self, vision_callback=None):
        self.vision = vision_callback
        self.is_sandboxed = True
        self.recording = []

    async def capture(self):
        if not HAS_PYAUTOGUI:
            return {"error": "pyautogui not installed"}
        screenshot = pyautogui.screenshot()
        return screenshot

    async def execute_action(self, action, user_approval=True):
        if not HAS_PYAUTOGUI:
            return {"error": "pyautogui not installed"}
        atype = action.get("type")
        if atype == "click":
            pyautogui.click(action["x"], action["y"])
        elif atype == "type":
            pyautogui.write(action["text"], interval=0.05)
        elif atype == "keypress":
            pyautogui.hotkey(*action.get("keys",[]))
        elif atype == "scroll":
            pyautogui.scroll(action.get("clicks",3))
        self.recording.append(action)
        return {"status": "ok", "action": atype}

    def start_recording(self):
        self.recording = []

    def replay(self):
        for action in self.recording:
            self.execute_action(action, user_approval=False)

    def get_screen_size(self):
        if HAS_PYAUTOGUI:
            return {"width": pyautogui.size().width, "height": pyautogui.size().height}
        return {"error": "pyautogui not available"}
