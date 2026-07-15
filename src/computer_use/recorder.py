"""ActionRecorder - record and replay CU actions."""
import json, time

class ActionRecorder:
    def __init__(self):
        self._actions = []
        self._start_time = None

    def start(self):
        self._actions = []
        self._start_time = time.time()

    def record(self, action):
        self._actions.append({"timestamp": time.time() - (self._start_time or 0), "action": action})

    def save(self, filepath):
        with open(filepath, "w") as f:
            json.dump({"actions": self._actions, "start_time": self._start_time}, f, indent=2)

    def load(self, filepath):
        with open(filepath) as f:
            data = json.load(f)
            self._actions = data.get("actions",[])
            self._start_time = data.get("start_time")
        return self._actions

    def get_actions(self):
        return self._actions
