"""WebSearchTool - web search integration placeholder."""
from src.tools.base import Tool

class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web for information"
    parameters_schema = {"type":"object","properties":{"query":{"type":"string"},"max_results":{"type":"integer","default":5}},"required":["query"]}

    async def execute(self, query, max_results=5):
        return {"query": query, "results": [], "note": "Web search requires an API key (Google Custom Search, Bing, etc.). Configure in Settings."}
