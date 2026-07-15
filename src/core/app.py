"""OpenShelf - QApplication 生命周期管理，独立异步线程。"""
import sys
import asyncio
import ctypes
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon

_WINDOW_CLASS_GUID = "{D98A4B3C-7F15-4E8C-A12D-5E6B7F8A9C0D}"


class AsyncWorker(QThread):
    """独立 QThread，运行 asyncio 事件循环。"""
    ready = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._loop = None
        self._running = False

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._running = True
        self.ready.emit()
        try:
            self._loop.run_forever()
        finally:
            pending = asyncio.all_tasks(self._loop)
            for task in pending:
                task.cancel()
            self._loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
            )
            self._loop.close()

    def get_loop(self):
        return self._loop

    def stop(self):
        self._running = False
        if self._loop and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._loop.stop)


class OpenShelfApp:
    """应用控制器。UI 在主线程，asyncio 在 AsyncWorker 线程。"""

    def __init__(self, argv=None):
        self._qt_app = None
        self._argv = argv or sys.argv
        self._mutex = None
        self._duplicate = False
        self._async_worker = None

    def initialize(self):
        """创建 QApplication，启动异步工作线程。"""
        self._qt_app = QApplication(self._argv)
        self._qt_app.setApplicationName("OpenShelf")
        self._qt_app.setOrganizationName("OpenShelf")
        self._qt_app.setApplicationVersion("1.0.0")

        icon_path = Path(__file__).parent.parent.parent / "resources" / "icons" / "app_icon.ico"
        if icon_path.exists() and icon_path.stat().st_size > 0:
            self._qt_app.setWindowIcon(QIcon(str(icon_path)))

        self._ensure_single_instance()

        self._async_worker = AsyncWorker()
        self._async_worker.start()
        return self._qt_app

    def _ensure_single_instance(self):
        try:
            kernel32 = ctypes.windll.kernel32
            self._mutex = kernel32.CreateMutexW(None, False, _WINDOW_CLASS_GUID)
            if kernel32.GetLastError() == 183:
                self._duplicate = True
        except Exception:
            pass

    def is_duplicate(self):
        return self._duplicate

    def get_async_loop(self):
        if self._async_worker is None:
            return None
        if self._async_worker.get_loop() is None:
            self._async_worker.wait(1000)
        return self._async_worker.get_loop()

    def run(self):
        if self._duplicate:
            return 0
        return self._qt_app.exec()

    async def cleanup(self):
        if self._async_worker:
            self._async_worker.stop()
            self._async_worker.wait(3000)
        if self._mutex:
            try:
                kernel32 = ctypes.windll.kernel32
                kernel32.CloseHandle(self._mutex)
            except Exception:
                pass
