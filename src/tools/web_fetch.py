"""WebFetchTool - fetch web page content."""
import aiohttp
from src.tools.base import Tool

class WebFetchTool(Tool):
    name = "web_fetch"
    description = "Fetch content from a URL"
    parameters_schema = {"type":"object","properties":{"url":{"type":"string"},"method":{"type":"string","default":"GET"}},"required":["url"]}

    async def execute(self, url, method="GET"):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, timeout=30) as resp:
                    text = await resp.text()
                    return {"url": url, "status": resp.status, "content": text[:50000], "content_type": resp.headers.get("content-type","")}
        except Exception as e:
            return {"error": str(e)}
