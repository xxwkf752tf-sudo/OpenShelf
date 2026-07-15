"""PluginRegistry - register plugin tool/command extensions."""
class PluginRegistry:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._extensions = {}
        return cls._instance

    def register_extension(self, name, obj):
        self._extensions[name] = obj

    def get(self, name):
        return self._extensions.get(name)

    def list_all(self):
        return list(self._extensions.keys())
