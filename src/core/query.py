"""QueryEngine - session and query management."""
import uuid, json
from src.api.base import ChatMessage
from src.core.storage import Database

class QueryEngine:
    def __init__(self, agent_loop, storage=None):
        self._agent = agent_loop
        self._db = storage or Database()
        self._current_conversation_id = agent_loop.conversation_id

    def start_new_conversation(self, title="", project_path=""):
        cid = str(uuid.uuid4())
        self._agent.conversation = []
        self._agent.conversation_id = cid
        self._current_conversation_id = cid
        self._db.create_conversation(cid, title, project_path)
        return cid

    def load_conversation(self, conversation_id):
        conv = self._db.get_conversation(conversation_id)
        if conv is None:
            return {"error": "Conversation not found"}
        messages = self._db.get_messages(conversation_id)
        self._agent.conversation = []
        for m in messages:
            tc = json.loads(m.get("tool_calls","")) if m.get("tool_calls") else None
            self._agent.conversation.append(ChatMessage(role=m["role"], content=m.get("content",""), tool_calls=tc))
        self._agent.conversation_id = conversation_id
        self._current_conversation_id = conversation_id
        return {"status": "loaded", "conversation_id": conversation_id, "count": len(messages), "title": conv.get("title","")}

    def export_conversation(self, conversation_id=None, fmt="markdown"):
        cid = conversation_id or self._current_conversation_id
        messages = self._db.get_messages(cid)
        conv = self._db.get_conversation(cid)
        if fmt == "markdown":
            lines = [f"# {conv.get('title','Conversation')}", f"Created: {conv.get('created_at','')}", ""]
            for m in messages:
                lines.append(f"### {m['role']}")
                lines.append(m.get("content",""))
            return "\n".join(lines)
        return json.dumps({"conversation": conv, "messages": messages}, indent=2, ensure_ascii=False)

    def search(self, query, limit=50):
        return self._db.search_messages(query, limit)
