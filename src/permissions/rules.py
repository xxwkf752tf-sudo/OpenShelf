"""PermissionRule - rule engine for tool execution permissions."""
from dataclasses import dataclass
from enum import Enum

class PermissionMode(Enum):
    ASK = "ask"
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class PermissionRule:
    name: str
    tool_pattern: str
    mode: PermissionMode = PermissionMode.ASK
    path_pattern: str = ""
    description: str = ""

class PermissionRegistry:
    def __init__(self):
        self._rules = []
        self._defaults()

    def _defaults(self):
        self._rules = [
            PermissionRule("read-files","file_read",PermissionMode.ALLOW,"","Allow reading files"),
            PermissionRule("write-files","file_write",PermissionMode.ASK,"","Ask before writing files"),
            PermissionRule("shell","bash",PermissionMode.ASK,"","Ask before shell commands"),
            PermissionRule("shell-powershell","powershell",PermissionMode.ASK,"","Ask before PowerShell"),
            PermissionRule("web-safe","web_fetch",PermissionMode.ALLOW,"","Allow web fetches"),
        ]

    def check(self, tool_name, path=None):
        import fnmatch
        for rule in self._rules:
            if fnmatch.fnmatch(tool_name, rule.tool_pattern):
                if rule.mode == PermissionMode.DENY:
                    return PermissionMode.DENY, rule
                if rule.mode == PermissionMode.ALLOW:
                    return PermissionMode.ALLOW, rule
        return PermissionMode.ASK, None
