"""PluginManager - hot-load Python module plugins."""
import importlib, sys
from pathlib import Path

class PluginManager:
    def __init__(self):
        self._plugins = {}
        self._plugin_dir = Path(__file__).parent / "bundled"

    def discover(self, search_path=None):
        sp = Path(search_path) if search_path else self._plugin_dir
        if not sp.exists():
            return []
        found = []
        for f in sp.glob("*.py"):
            if f.stem in ("__init__",): continue
            found.append(str(f))
        for d in sp.glob("*/"):
            init = d / "__init__.py"
            if init.exists():
                found.append(str(init.parent))
        return found

    def load(self, plugin_path):
        pp = Path(plugin_path)
        if pp.is_file():
            name = pp.stem
        else:
            name = pp.name
        try:
            spec = importlib.util.spec_from_file_location(f"openshelf_plugin_{name}", str(pp / "__init__.py") if pp.is_dir() else str(pp))
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)
            if hasattr(mod, "register"):
                self._plugins[name] = mod
                mod.register()
                return {"status": "loaded", "name": name}
            return {"status": "error", "error": "No register() function found"}
        except Exception as e:
            return {"status": "error", "name": name, "error": str(e)}

    def unload(self, name):
        mod = self._plugins.pop(name, None)
        if mod and hasattr(mod, "unregister"):
            mod.unregister()
        return {"status": "unloaded", "name": name}

    def list_plugins(self):
        return list(self._plugins.keys())
