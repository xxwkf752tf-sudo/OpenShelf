"""Task management tools - create, list, get, stop, update tasks."""
from src.tools.base import Tool
import uuid
from datetime import datetime

class TaskManager:
    _tasks = {}

class TaskCreateTool(Tool):
    name = "task_create"
    description = "Create a new background task or sub-agent"
    parameters_schema = {"type":"object","properties":{"description":{"type":"string"},"subagent_type":{"type":"string","default":"general"},"prompt":{"type":"string"}},"required":["description","prompt"]}
    async def execute(self, description, prompt, subagent_type="general"):
        tid = str(uuid.uuid4())[:8]
        TaskManager._tasks[tid] = {"id":tid,"description":description,"type":subagent_type,"prompt":prompt,"status":"pending","created_at":datetime.utcnow().isoformat(),"result":None}
        return {"task_id": tid, "status": "created"}

class TaskListTool(Tool):
    name = "task_list"
    description = "List all tasks"
    parameters_schema = {"type":"object","properties":{},"required":[]}
    async def execute(self):
        return {"tasks": list(TaskManager._tasks.values())}

class TaskGetTool(Tool):
    name = "task_get"
    description = "Get task details"
    parameters_schema = {"type":"object","properties":{"task_id":{"type":"string"}},"required":["task_id"]}
    async def execute(self, task_id):
        t = TaskManager._tasks.get(task_id)
        return t if t else {"error": "Task not found"}
