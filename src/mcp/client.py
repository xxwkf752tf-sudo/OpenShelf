"""MCPClient - full MCP protocol client implementation."""
import asyncio, json, uuid
from src.mcp.protocol import MCPProtocol

class MCPClient:
    def __init__(self, server_config):
        self.name = server_config["name"]
        self.transport_type = server_config.get("transport","stdio")
        self.command = server_config.get("command")
        self.args = server_config.get("args",[])
        self.url = server_config.get("url")
        self.env_vars = server_config.get("env_vars",{})
        self._process = None
        self._session = None
        self._request_id = 0
        self._tools = []
        self._resources = []
        self._initialized = False

    async def connect(self):
        if self.transport_type == "stdio":
            env = {**dict(__import__("os").environ), **self.env_vars}
            self._process = await asyncio.create_subprocess_exec(self.command, *self.args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
            self._transport = __import__("src.mcp.transport", fromlist=["StdioTransport"]).StdioTransport(self._process)
        elif self.transport_type in ("http","sse"):
            import aiohttp
            self._session = aiohttp.ClientSession()
            self._transport = __import__("src.mcp.transport", fromlist=["HttpTransport"]).HttpTransport(self.url, self._session)
        await self._initialize()

    async def _initialize(self):
        resp = await self._send(MCPProtocol.request("initialize", {"protocolVersion":"2024-11-05","capabilities":{"tools":{},"resources":{}}}, self._next_id()))
        await self._send(MCPProtocol.notification("notifications/initialized",{}))
        self._initialized = True
        await self._discover()

    async def _discover(self):
        tools = await self._send(MCPProtocol.request("tools/list",{},self._next_id()))
        self._tools = tools.get("tools",[])
        resources = await self._send(MCPProtocol.request("resources/list",{},self._next_id()))
        self._resources = resources.get("resources",[])

    def _next_id(self):
        self._request_id += 1
        return self._request_id

    async def _send(self, message):
        encoded = MCPProtocol.encode(message)
        if self.transport_type == "stdio":
            return await self._transport.send_std(encoded)
        return await self._transport.send(encoded)

    async def call_tool(self, name, arguments):
        return await self._send(MCPProtocol.request("tools/call",{"name":name,"arguments":arguments},self._next_id()))

    async def read_resource(self, uri):
        return await self._send(MCPProtocol.request("resources/read",{"uri":uri},self._next_id()))

    async def disconnect(self):
        if self._transport:
            await self._transport.close()
            self._transport = None

    @property
    def tools(self): return self._tools
    @property
    def resources(self): return self._resources
