"""GlobTool - file pattern matching."""
from pathlib import Path
from src.tools.base import Tool

class GlobTool(Tool):
    name = "glob"
    description = "Find files matching a glob pattern"
    parameters_schema = {"type":"object","properties":{"pattern":{"type":"string","description":"Glob pattern like **/*.py"},"path":{"type":"string","default":"."}},"required":["pattern"]}

    async def execute(self, pattern, path="."):
        base = Path(path).resolve()
        matches = sorted(base.glob(pattern))
        return {"matches": [str(m.relative_to(base)) for m in matches if m.is_file()], "base": str(base), "count": len([m for m in matches if m.is_file()])}
