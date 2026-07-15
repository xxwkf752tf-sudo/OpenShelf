"""FileWriteTool - write file with diff preview support."""
import difflib, tempfile, shutil
from pathlib import Path
from src.tools.base import Tool

class FileWriteTool(Tool):
    name = "file_write"
    description = "Write contents to a file, creating or overwriting"
    parameters_schema = {"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"},"encoding":{"type":"string","default":"utf-8"},"backup":{"type":"boolean","default":True}},"required":["path","content"]}

    async def execute(self, path, content, encoding="utf-8", backup=True):
        p = Path(path)
        diff = ""
        old_content = ""
        if p.exists():
            old_content = p.read_text(encoding=encoding)
            diff = "".join(difflib.unified_diff(old_content.splitlines(True), content.splitlines(True), fromfile=str(p), tofile=str(p)))
        if backup and p.exists():
            backup_path = p.with_suffix(p.suffix + ".bak")
            shutil.copy2(p, backup_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding=encoding)
        return {"path": str(p.resolve()), "written": len(content), "diff": diff, "had_previous": bool(old_content)}
