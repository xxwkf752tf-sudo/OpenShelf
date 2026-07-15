"""GrepTool - search text in files."""
import subprocess
from src.tools.base import Tool

class GrepTool(Tool):
    name = "grep"
    description = "Search for a pattern in files"
    parameters_schema = {"type":"object","properties":{"pattern":{"type":"string"},"path":{"type":"string","default":"."},"include":{"type":"string","default":"*.*"},"max_results":{"type":"integer","default":50}},"required":["pattern"]}

    async def execute(self, pattern, path=".", include="*.*", max_results=50):
        try:
            result = subprocess.run(["rg","--line-number","--max-count",str(max_results),"-g",include,pattern,path], capture_output=True, text=True, timeout=30, cwd=path)
            lines = result.stdout.strip().split("\n")[:max_results]
            return {"matches": [l for l in lines if l], "count": len([l for l in lines if l]), "pattern": pattern}
        except FileNotFoundError:
            return {"error": "ripgrep (rg) not found. Install from https://github.com/BurntSushi/ripgrep"}
