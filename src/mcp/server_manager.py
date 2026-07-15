"""MCPServerManager - lifecycle management for multiple MCP servers."""
import asyncio
from src.mcp.client import MCPClient

class MCPServerManager:
    def __init__(self, storage):
        self._storage = storage
        self._clients = {}
        self._shared_memory = {}

    async def start_all(self):
        servers = self._storage.get_mcp_servers(enabled_only=True)
        for srv in servers:
            try:
                client = MCPClient(srv)
                await client.connect()
                self._clients[srv["id"]] = client
            except Exception as e:
                print(f"MCP server {srv.get('name')} failed: {e}")

    async def start_one(self, server_id):
        servers = self._storage.get_mcp_servers(enabled_only=False)
        srv = next((s for s in servers if s["id"] == server_id), None)
        if not srv: return {"error": "Server not found"}
        try:
            client = MCPClient(srv)
            await client.connect()
            self._clients[server_id] = client
            return {"status": "connected", "tools": len(client.tools), "resources": len(client.resources)}
        except Exception as e:
            return {"error": str(e)}

    async def stop_one(self, server_id):
        client = self._clients.pop(server_id, None)
        if client:
            await client.disconnect()
            return {"status": "disconnected"}
        return {"error": "Server not running"}

    async def call_tool(self, server_name, tool_name, arguments):
        for client in self._clients.values():
            if client.name == server_name:
                return await client.call_tool(tool_name, arguments)
        return {"error": f"Server {server_name} not connected"}

    def get_all_tools(self):
        tools = {}
        for cid, client in self._clients.items():
            for tool in client.tools:
                tools[f"{client.name}/{tool.get('name','unknown')}"] = tool
        return tools

    def get_shared_memory(self, key):
        return self._shared_memory.get(key)

    def set_shared_memory(self, key, value):
        self._shared_memory[key] = value

    async def disconnect_all(self):
        for client in self._clients.values():
            await client.disconnect()
        self._clients.clear()
