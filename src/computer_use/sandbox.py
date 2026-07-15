"""CUSandbox - sandboxed execution environment for Computer Use."""
import tempfile, os
from pathlib import Path

class CUSandbox:
    def __init__(self):
        self._allowed_paths = []
        self._blocked_actions = ["delete", "format", "restart", "shutdown"]
        self._temp_dir = Path(tempfile.mkdtemp(prefix="openshelf_cu_"))

    def allow_path(self, path):
        self._allowed_paths.append(Path(path).resolve())

    def is_allowed(self, action):
        return action.get("type","") not in self._blocked_actions

    def cleanup(self):
        import shutil
        if self._temp_dir.exists():
            shutil.rmtree(self._temp_dir, ignore_errors=True)
