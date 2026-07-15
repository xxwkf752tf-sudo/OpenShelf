"""FileReadTool - read file contents."""
from pathlib import Path
from src.tools.base import Tool

class FileReadTool(Tool):
    name = "file_read"
    description = "Read the contents of a file"
    parameters_schema = {"type":"object","properties":{"path":{"type":"string","description":"Path to the file"},"encoding":{"type":"string","default":"utf-8"}},"required":["path"]}

    async def execute(self, path, encoding="utf-8"):
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}
        try:
            content = p.read_text(encoding=encoding)
            return {"path": str(p.resolve()), "content": content, "size": p.stat().st_size}
        except Exception as e:
            return {"error": str(e)}
