"""RAGWatcher - file change monitoring for auto re-index."""
import time
from pathlib import Path

class RAGWatcher:
    def __init__(self, indexer=None, debounce_seconds=2):
        self._indexer = indexer
        self._debounce = debounce_seconds
        self._watched_dirs = set()
        self._running = False

    def watch(self, directory, extensions=None):
        self._watched_dirs.add((Path(directory), extensions))

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    async def _poll(self):
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            observer = Observer()
            class Handler(FileSystemEventHandler):
                def on_modified(self2, event):
                    if self._indexer and not event.is_directory:
                        try:
                            p = Path(event.src_path)
                            self._indexer.index_file(p, p.read_text(encoding="utf-8",errors="replace"), {"path": str(p)})
                        except Exception: pass
            for d, _ in self._watched_dirs:
                observer.schedule(Handler(), str(d), recursive=True)
            observer.start()
            while self._running:
                time.sleep(1)
            observer.stop()
            observer.join()
        except ImportError:
            pass
