"""ToolRegistry - singleton registry for tool discovery and invocation."""
class ToolRegistry:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    def register(self, tool):
        self._tools[tool.name] = tool

    def register_many(self, tools):
        for t in tools: self.register(t)

    def get(self, name):
        return self._tools.get(name)

    def list_all(self):
        return list(self._tools.values())

    def list_names(self):
        return list(self._tools.keys())

    def get_schemas(self):
        return [t.to_schema() for t in self._tools.values()]

    def unregister(self, name):
        self._tools.pop(name, None)
