"""DeepSeek provider with prefix-cache optimization."""
import aiohttp, hashlib, json
from src.api.base import LLMProvider, ChatMessage, ChatResponse, StreamEvent

class DeepSeekProvider(LLMProvider):
    provider_id = "deepseek"
    default_model = "deepseek-chat"
    supports_prefix_cache = True
    supports_tools = True

    def __init__(self, api_key, base_url="https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.fixed_prefix = []
        self._prefix_hash = ""
        self._last_usage = {}

    def set_fixed_prefix(self, system_messages):
        self.fixed_prefix = list(system_messages)
        self._prefix_hash = hashlib.sha256("".join(m.content if hasattr(m,"content") else str(m) for m in system_messages).encode()).hexdigest()[:16]

    def _build_payload(self, messages, stream=False, model=None, tools=None, max_tokens=4096, temperature=0.0):
        combined = list(self.fixed_prefix) + list(messages)
        msgs = []
        for m in combined:
            entry = {"role": m.role if hasattr(m,"role") else m["role"], "content": m.content if hasattr(m,"content") else m.get("content","")}
            if hasattr(m,"tool_call_id") and m.tool_call_id:
                entry["tool_call_id"] = m.tool_call_id
            if hasattr(m,"tool_calls") and m.tool_calls:
                entry["tool_calls"] = m.tool_calls
            if hasattr(m,"name") and m.name:
                entry["name"] = m.name
            msgs.append(entry)
        payload = {"model": model or self.default_model, "messages": msgs, "stream": stream, "max_tokens": max_tokens, "temperature": temperature}
        if tools: payload["tools"] = tools
        return payload

    async def chat(self, messages, model=None, tools=None, max_tokens=4096, temperature=0.0):
        payload = self._build_payload(messages, model=model, tools=tools, max_tokens=max_tokens, temperature=temperature)
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.base_url}/chat/completions", headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"}, json=payload) as resp:
                data = await resp.json()
                choice = data["choices"][0]
                usage = data.get("usage",{})
                self._last_usage = usage
                msg = choice.get("message", {})
                content = msg.get("content", "")
                tc_list = msg.get("tool_calls", [])
                return ChatResponse(id=data["id"], content=content, finish_reason=choice.get("finish_reason","stop"), usage=usage, model=data["model"], choices=[{"message": msg}])

    async def chat_stream(self, messages, model=None, tools=None, max_tokens=4096, temperature=0.0):
        payload = self._build_payload(messages, stream=True, model=model, tools=tools, max_tokens=max_tokens, temperature=temperature)
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.base_url}/chat/completions", headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"}, json=payload) as resp:
                buffer = ""
                tool_calls_acc = {}
                async for line in resp.content:
                    text = line.decode().strip()
                    if text.startswith("data: "):
                        segment = text[6:]
                        if segment == "[DONE]":
                            tc_list = [tool_calls_acc[k] for k in sorted(tool_calls_acc.keys())]
                            yield StreamEvent(type="done", content=buffer, usage=self._last_usage, tool_calls=tc_list)
                            return
                        try:
                            chunk = json.loads(segment)
                            delta = chunk["choices"][0].get("delta",{})
                            d_content = delta.get("content","")
                            if d_content:
                                buffer += d_content
                                yield StreamEvent(type="text_delta", delta=d_content)
                            # Accumulate tool calls
                            tc_deltas = delta.get("tool_calls", [])
                            for tc in tc_deltas:
                                idx = tc.get("index", 0)
                                if idx not in tool_calls_acc:
                                    tool_calls_acc[idx] = {"id": "", "type": "function", "function": {"name": "", "arguments": ""}}
                                if "id" in tc:
                                    tool_calls_acc[idx]["id"] = tc["id"]
                                if "function" in tc:
                                    fn = tc["function"]
                                    if "name" in fn and fn["name"]:
                                        tool_calls_acc[idx]["function"]["name"] = fn["name"]
                                    if "arguments" in fn:
                                        tool_calls_acc[idx]["function"]["arguments"] += fn["arguments"]
                            if "usage" in chunk:
                                self._last_usage = chunk["usage"]
                        except (json.JSONDecodeError, KeyError):
                            continue
                tc_list = [tool_calls_acc[k] for k in sorted(tool_calls_acc.keys())]
                yield StreamEvent(type="done", content=buffer, usage=self._last_usage, tool_calls=tc_list)

    def estimate_tokens(self, messages):
        total = 0
        for m in messages:
            c = m.content if hasattr(m,"content") else str(m)
            total += len(c) // 4
        return total

    def get_cache_hit_rate(self):
        usage = self._last_usage
        if not usage: return 0.0
        total = usage.get("prompt_tokens",0)
        cached = usage.get("prompt_cache_hit_tokens",0) + usage.get("cached_tokens",0)
        return cached / total if total > 0 else 0.0
