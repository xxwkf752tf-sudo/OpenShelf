"""Database - SQLite persistence layer."""
import sqlite3, json, os
from pathlib import Path
from datetime import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY, title TEXT NOT NULL DEFAULT "",
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
    project_path TEXT DEFAULT "", tags TEXT DEFAULT "[]"
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id TEXT NOT NULL,
    role TEXT NOT NULL, content TEXT, tool_calls TEXT,
    tool_results TEXT, created_at TEXT NOT NULL, model TEXT DEFAULT "",
    token_count INTEGER DEFAULT 0, cached_tokens INTEGER DEFAULT 0,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT DEFAULT "",
    instructions TEXT DEFAULT "", allowed_tools TEXT DEFAULT "[]",
    chain_to TEXT DEFAULT "[]", enabled INTEGER DEFAULT 1, source_path TEXT DEFAULT ""
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mcp_servers (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, transport TEXT DEFAULT "stdio",
    command TEXT DEFAULT "", args TEXT DEFAULT "[]", url TEXT DEFAULT "",
    env_vars TEXT DEFAULT "{}", enabled INTEGER DEFAULT 1
);
"""

class Database:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conn = None
            cls._instance._db_path = None
        return cls._instance

    def initialize(self, db_path=None):
        if db_path is None:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            db_dir = Path(appdata) / "OpenShelf"
            db_dir.mkdir(parents=True, exist_ok=True)
            self._db_path = db_dir / "openshelf.db"
        else:
            self._db_path = db_path
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    @property
    def conn(self):
        if self._conn is None: raise RuntimeError("Database not initialized.")
        return self._conn

    def create_conversation(self, cid, title="", project_path=""):
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            "INSERT INTO conversations(id,title,created_at,updated_at,project_path) VALUES(?,?,?,?,?)",
            (cid, title, now, now, project_path))
        self.conn.commit()

    def list_conversations(self, limit=50, offset=0):
        rows = self.conn.execute(
            "SELECT * FROM conversations ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            (limit, offset)).fetchall()
        return [dict(r) for r in rows]

    def get_conversation(self, cid):
        row = self.conn.execute("SELECT * FROM conversations WHERE id=?", (cid,)).fetchone()
        return dict(row) if row else None

    def delete_conversation(self, cid):
        self.conn.execute("DELETE FROM messages WHERE conversation_id=?", (cid,))
        self.conn.execute("DELETE FROM conversations WHERE id=?", (cid,))
        self.conn.commit()

    def add_message(self, conversation_id, role, content="", tool_calls="",
                    tool_results="", model="", token_count=0, cached_tokens=0):
        now = datetime.utcnow().isoformat()
        cursor = self.conn.execute(
            "INSERT INTO messages(conversation_id,role,content,tool_calls,tool_results,created_at,model,token_count,cached_tokens) VALUES(?,?,?,?,?,?,?,?,?)",
            (conversation_id, role, content, tool_calls, tool_results, now, model, token_count, cached_tokens))
        self.conn.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conversation_id))
        self.conn.commit()
        return cursor.lastrowid

    def get_messages(self, conversation_id, limit=200):
        rows = self.conn.execute(
            "SELECT * FROM messages WHERE conversation_id=? ORDER BY id ASC LIMIT ?",
            (conversation_id, limit)).fetchall()
        return [dict(r) for r in rows]

    def get_setting(self, key, default=""):
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def set_setting(self, key, value):
        now = datetime.utcnow().isoformat()
        self.conn.execute("INSERT OR REPLACE INTO settings(key,value,updated_at) VALUES(?,?,?)", (key, value, now))
        self.conn.commit()

    def save_skill(self, skill):
        self.conn.execute(
            "INSERT OR REPLACE INTO skills(id,name,description,instructions,allowed_tools,chain_to,enabled,source_path) VALUES(?,?,?,?,?,?,?,?)",
            (skill["id"], skill["name"], skill.get("description",""),
             skill.get("instructions",""), json.dumps(skill.get("allowed_tools",[])),
             json.dumps(skill.get("chain_to",[])), int(skill.get("enabled",True)),
             skill.get("source_path","")))
        self.conn.commit()

    def get_skills(self, enabled_only=True):
        q = "SELECT * FROM skills" + (" WHERE enabled=1" if enabled_only else "")
        rows = self.conn.execute(q).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["allowed_tools"] = json.loads(d.get("allowed_tools","[]"))
            d["chain_to"] = json.loads(d.get("chain_to","[]"))
            results.append(d)
        return results

    def save_mcp_server(self, srv):
        self.conn.execute(
            "INSERT OR REPLACE INTO mcp_servers(id,name,transport,command,args,url,env_vars,enabled) VALUES(?,?,?,?,?,?,?,?)",
            (srv["id"], srv["name"], srv.get("transport","stdio"),
             srv.get("command",""), json.dumps(srv.get("args",[])),
             srv.get("url",""), json.dumps(srv.get("env_vars",{})),
             int(srv.get("enabled",True))))
        self.conn.commit()

    def get_mcp_servers(self, enabled_only=True):
        q = "SELECT * FROM mcp_servers" + (" WHERE enabled=1" if enabled_only else "")
        rows = self.conn.execute(q).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["args"] = json.loads(d.get("args","[]"))
            d["env_vars"] = json.loads(d.get("env_vars","{}"))
            results.append(d)
        return results

    def delete_mcp_server(self, sid):
        self.conn.execute("DELETE FROM mcp_servers WHERE id=?", (sid,))
        self.conn.commit()

    def close(self):
        if self._conn: self._conn.close(); self._conn = None
