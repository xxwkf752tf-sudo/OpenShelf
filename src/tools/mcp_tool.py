"""MCPTool - bridge for calling MCP server tools."""
from src.tools.base import Tool

class MCPTool(Tool):
    name = "mcp_call"
    description = "Call a tool on a connected MCP server"
    parameters_schema = {"type":"object","properties":{"server":{"type":"string"},"tool_name":{"type":"string"},"arguments":{"type":"object","default":{}}},"required":["server","tool_name"]}

    def __init__(self, mcp_manager=None):
        self._mcp_manager = mcp_manager

    async def execute(self, server, tool_name, arguments=None):
        if self._mcp_manager is None:
            return {"error": "MCP manager not initialized"}
        result = await self._mcp_manager.call_tool(server, tool_name, arguments or {})
        return result
