"""MCP transports: stdio and HTTP."""
import asyncio, json

class StdioTransport:
    def __init__(self, process):
        self._process = process

    async def send(self, message):
        data = json.dumps(message) + "\n"
        self._process.stdin.write(data.encode())
        await self._process.stdin.drain()

    async def receive(self):
        line = await self._process.stdout.readline()
        return json.loads(line.decode())

    async def close(self):
        if self._process:
            self._process.terminate()

class HttpTransport:
    def __init__(self, url, session=None):
        self.url = url
        self._session = session

    async def send(self, message):
        import aiohttp
        if self._session is None:
            self._session = aiohttp.ClientSession()
        async with self._session.post(self.url, json=message) as resp:
            return await resp.json()

    async def close(self):
        if self._session:
            await self._session.close()

class SseTransport:
    def __init__(self, url, session=None):
        self.url = url
        self._session = session

    async def stream(self, message):
        import aiohttp
        if self._session is None:
            self._session = aiohttp.ClientSession()
        async with self._session.post(self.url, json=message) as resp:
            async for line in resp.content:
                text = line.decode().strip()
                if text.startswith("data: "):
                    yield json.loads(text[6:])

    async def close(self):
        if self._session:
            await self._session.close()
