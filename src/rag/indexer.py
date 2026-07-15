"""RAGIndexer - file indexing using sentence-transformers + chromadb."""
import os
from pathlib import Path
import hashlib

class RAGIndexer:
    def __init__(self, index_dir=None):
        if index_dir is None:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            index_dir = Path(appdata) / "OpenShelf" / "rag_index"
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._collection = None

    def initialize(self):
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(self.index_dir))
            self._collection = client.get_or_create_collection("project_files")
            return True
        except ImportError:
            return False

    def index_file(self, filepath, content, metadata=None):
        if self._collection is None:
            return False
        file_hash = hashlib.md5(content.encode()).hexdigest()
        self._collection.add(documents=[content], metadatas=[metadata or {"path": str(filepath)}], ids=[file_hash])
        return True

    def index_directory(self, root_path, extensions=None):
        if self._collection is None:
            return {"error": "RAG not initialized"}
        root = Path(root_path)
        indexed = 0
        for f in root.rglob("*"):
            if f.is_file() and (extensions is None or f.suffix in extensions):
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                    self.index_file(f, content, {"path": str(f), "size": f.stat().st_size})
                    indexed += 1
                except Exception:
                    pass
        return {"indexed_files": indexed}

    def query(self, text, n_results=5):
        if self._collection is None:
            return []
        results = self._collection.query(query_texts=[text], n_results=n_results)
        return [{"content": d, "metadata": m} for d, m in zip(results.get("documents",[[]])[0], results.get("metadatas",[[]])[0])]
