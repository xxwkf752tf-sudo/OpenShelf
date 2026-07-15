"""PermissionManager - permission checking and user prompts."""
from src.permissions.rules import PermissionRegistry, PermissionMode

class PermissionManager:
    def __init__(self):
        self._registry = PermissionRegistry()

    async def check(self, tool_name, arguments=None, callback=None):
        mode, rule = self._registry.check(tool_name, arguments)
        if mode == PermissionMode.ALLOW:
            return True
        if mode == PermissionMode.DENY:
            return False
        if callback:
            return await callback(tool_name, arguments, rule)
        return True

    def add_rule(self, rule):
        self._registry._rules.append(rule)
