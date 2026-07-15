"""TerminalManager - multi-tab terminal session management."""
from src.terminal.session import TerminalSession
import uuid

class TerminalManager:
    def __init__(self):
        self._sessions = {}

    def create_session(self, cwd=None):
        tid = str(uuid.uuid4())[:8]
        session = TerminalSession()
        session.start(cwd=cwd)
        self._sessions[tid] = session
        return tid, session

    def get_session(self, tid):
        return self._sessions.get(tid)

    def close_session(self, tid):
        session = self._sessions.pop(tid, None)
        if session:
            session.terminate()

    def close_all(self):
        for session in self._sessions.values():
            session.terminate()
        self._sessions.clear()

    def list_sessions(self):
        return [{"id": tid, "alive": s.is_alive()} for tid, s in self._sessions.items()]
