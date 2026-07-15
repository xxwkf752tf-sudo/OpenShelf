"""OpenAI-compatible provider for Ollama, Groq, vLLM, etc."""
import aiohttp, json
from src.api.base import LLMProvider, ChatMessage, ChatResponse, StreamEvent

class OpenAICompatProvider(LLMProvider):
    supports_tools = True

    def __init__(self, provider_id, api_key, base_url, default_model="gpt-4o"):
        self.provider_id = provider_id
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self._last_usage = {}

    def _build_payload(self, messages, stream=False, model=None, tools=None, max_tokens=4096, temperature=0.0):
        msgs = []
        for m in messages:
            entry = {"role": m.role if hasattr(m,"role") else m["role"], "content": m.content if hasattr(m,"content") else m.get("content","")}
            if hasattr(m,"tool_call_id") and m.tool_call_id:
                entry["tool_call_id"] = m.tool_call_id
            msgs.append(entry)
        payload = {"model": model or self.default_model, "messages": msgs, "stream": stream, "max_tokens": max_tokens, "temperature": temperature}
        if tools: payload["tools"] = tools
        return payload

    async def chat(self, messages, model=None, tools=None, max_tokens=4096, temperature=0.0):
        payload = self._build_payload(messages, model=model, tools=tools, max_tokens=max_tokens, temperature=temperature)
        headers = {"Content-Type":"application/json"}
        if self.api_key and self.api_key != "ollama":
            headers["Authorization"] = f"Bearer {self.api_key}"
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.base_url}/chat/completions", headers=headers, json=payload) as resp:
                data = await resp.json()
                choice = data["choices"][0]
                usage = data.get("usage",{})
                self._last_usage = usage
                return ChatResponse(id=data.get("id",""), content=choice["message"]["content"], finish_reason=choice.get("finish_reason","stop"), usage=usage, model=data.get("model",""))

    async def chat_stream(self, messages, model=None, tools=None, max_tokens=4096, temperature=0.0):
        payload = self._build_payload(messages, stream=True, model=model, tools=tools, max_tokens=max_tokens, temperature=temperature)
        headers = {"Content-Type":"application/json"}
        if self.api_key and self.api_key != "ollama":
            headers["Authorization"] = f"Bearer {self.api_key}"
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.base_url}/chat/completions", headers=headers, json=payload) as resp:
                buffer = ""
                async for line in resp.content:
                    text = line.decode().strip()
                    if text.startswith("data: "):
                        segment = text[6:]
                        if segment == "[DONE]":
                            yield StreamEvent(type="done", content="", usage=self._last_usage)
                            return
                        try:
                            chunk = json.loads(segment)
                            delta = chunk["choices"][0].get("delta",{})
                            d = delta.get("content","")
                            if d: buffer += d; yield StreamEvent(type="text_delta", delta=d)
                            if "usage" in chunk: self._last_usage = chunk["usage"]
                        except: continue
                yield StreamEvent(type="done", content=buffer, usage=self._last_usage)

    def estimate_tokens(self, messages):
        return sum(len((m.content if hasattr(m,"content") else str(m))) // 4 for m in messages)
