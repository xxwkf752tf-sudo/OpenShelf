"""SSE/StreamableHTTP async transport utilities."""
import asyncio, json
import aiohttp

class SSETransport:
    @staticmethod
    async def stream(url, headers=None, body=None, method="POST"):
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers or {}, json=body) as resp:
                async for line in resp.content:
                    text = line.decode().strip()
                    if text.startswith("data: "):
                        data = text[6:]
                        if data == "[DONE]":
                            return
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            yield data

class HttpTransport:
    @staticmethod
    async def request(url, headers=None, body=None, method="POST"):
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers or {}, json=body) as resp:
                return await resp.json()
