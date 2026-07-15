"""FileOps - filesystem operations with backup/undo."""
import shutil, tempfile
from pathlib import Path

class FileOps:
    @staticmethod
    def read_file(filepath, encoding="utf-8"):
        p = Path(filepath)
        return p.read_text(encoding=encoding) if p.exists() else None

    @staticmethod
    def write_file(filepath, content, encoding="utf-8", backup=True):
        p = Path(filepath)
        if backup and p.exists():
            backup_path = p.with_suffix(p.suffix + ".bak")
            shutil.copy2(p, backup_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding=encoding)
        return str(p.resolve())

    @staticmethod
    def delete_file(filepath, backup=True):
        p = Path(filepath)
        if not p.exists(): return False
        if backup:
            backup_path = p.with_suffix(p.suffix + ".delbak")
            shutil.copy2(p, backup_path)
        p.unlink()
        return True

    @staticmethod
    def list_dir(dirpath, pattern="*"):
        p = Path(dirpath)
        return [{"name": f.name, "is_dir": f.is_dir(), "size": f.stat().st_size if f.is_file() else 0} for f in p.glob(pattern)]

    @staticmethod
    def get_diff(filepath, new_content):
        import difflib
        p = Path(filepath)
        old = p.read_text() if p.exists() else ""
        diff = "".join(difflib.unified_diff(old.splitlines(True), new_content.splitlines(True), fromfile=str(p), tofile=str(p)))
        return diff

    @staticmethod
    def batch_write(operations):
        results = []
        backup_files = []
        for op in operations:
            try:
                p = Path(op["path"])
                if op.get("backup",True) and p.exists():
                    backup_files.append(p)
                FileOps.write_file(op["path"], op["content"], backup=op.get("backup",True))
                results.append({"path": op["path"], "status": "ok"})
            except Exception as e:
                results.append({"path": op["path"], "status": "error", "error": str(e)})
        return results
