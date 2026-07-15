"""CommandCompleter - smart command path completion."""
import os
from pathlib import Path

class CommandCompleter:
    def __init__(self):
        self._command_cache = []

    def complete(self, partial):
        results = []
        cwd = Path.cwd()
        for f in cwd.iterdir():
            name = f.name
            if name.startswith(partial):
                results.append(name + ("/" if f.is_dir() else ""))
        return sorted(results)[:20]

    def get_path_completions(self, partial):
        expanded = os.path.expandvars(os.path.expanduser(partial))
        base = Path(expanded)
        search_dir = base.parent if not str(partial).endswith("/") else base
        if not search_dir.exists():
            search_dir = Path.cwd()
        prefix = base.name
        results = []
        for f in search_dir.iterdir():
            if f.name.startswith(prefix):
                p = str(f.relative_to(Path.cwd())).replace("\\", "/")
                results.append(p + ("/" if f.is_dir() else ""))
        return sorted(results)[:20]
