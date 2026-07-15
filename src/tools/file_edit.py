"""FileEditTool - sed-style find-and-replace editing."""
from pathlib import Path
from src.tools.base import Tool

class FileEditTool(Tool):
    name = "file_edit"
    description = "Edit a file by replacing a specific text pattern"
    parameters_schema = {"type":"object","properties":{"path":{"type":"string"},"old_string":{"type":"string"},"new_string":{"type":"string"},"encoding":{"type":"string","default":"utf-8"}},"required":["path","old_string","new_string"]}

    async def execute(self, path, old_string, new_string, encoding="utf-8"):
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}
        content = p.read_text(encoding=encoding)
        if old_string not in content:
            return {"error": "old_string not found in file"}
        new_content = content.replace(old_string, new_string, 1)
        p.write_text(new_content, encoding=encoding)
        return {"path": str(p.resolve()), "replaced": True}
