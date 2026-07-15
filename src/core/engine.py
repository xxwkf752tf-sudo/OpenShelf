"""AgentLoop - Core async agent execution loop."""
import asyncio, json, re, uuid
from datetime import datetime
from src.api.base import ChatMessage
from src.core.context import ContextManager
from src.core.storage import Database

class AgentLoop:
    MAX_TURNS = 50

    def __init__(self, provider, tool_registry):
        self.provider = provider
        self.tool_registry = tool_registry
        self.context_mgr = ContextManager()
        self.system_prompt = ""
        self.conversation = []
        self.conversation_id = str(uuid.uuid4())
        self._db = Database()
        self._is_running = False
        self._cancel_requested = False
        self._total_tokens = {"prompt": 0, "completion": 0, "cached": 0}

    def set_system_prompt(self, prompt, skills_instructions=None):
        full = prompt
        if skills_instructions:
            for si in skills_instructions:
                full += "\n\n<skill_instructions>\n" + si + "\n</skill_instructions>"
        self.system_prompt = full

    def cancel(self):
        self._cancel_requested = True

    async def run(self, user_input, max_turns=None, callback=None):
        if max_turns is None:
            max_turns = self.MAX_TURNS
        self._is_running = True
        self._cancel_requested = False
        self.conversation.append(ChatMessage(role="user", content=user_input))
        self._db.add_message(self.conversation_id, "user", user_input)

        for turn in range(max_turns):
            if self._cancel_requested:
                yield {"type": "cancelled"}
                break

            messages = [ChatMessage(role="system", content=self.system_prompt)]
            messages.extend(self.conversation)
            tools = self.tool_registry.get_schemas() if len(self.tool_registry.list_all()) > 0 else None

            content_buffer = ""
            stream_tool_calls = []
            async for event in self.provider.chat_stream(messages, tools=tools):
                if self._cancel_requested:
                    break
                if event.type == "text_delta":
                    content_buffer += event.delta
                    yield {"type": "text_delta", "content": event.delta}
                elif event.type == "done":
                    if event.usage:
                        self._total_tokens["prompt"] += event.usage.get("prompt_tokens", 0)
                        self._total_tokens["completion"] += event.usage.get("completion_tokens", 0)
                        self._total_tokens["cached"] += event.usage.get("cached_tokens", 0)
                    if event.tool_calls:
                        stream_tool_calls = event.tool_calls

            tool_calls = []
            if stream_tool_calls:
                for tc in stream_tool_calls:
                    fn = tc.get("function", {})
                    args = fn.get("arguments", "{}")
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except (json.JSONDecodeError, ValueError):
                            args = {}
                    tool_calls.append({"id": tc.get("id", f"call_{len(tool_calls)}"), "name": fn.get("name", ""), "arguments": args})
            # If streaming gave empty tool calls, try non-streaming
            if not tool_calls and content_buffer:
                tool_calls = self._parse_tool_calls(content_buffer)
            # If still empty and we expect tool calls, use non-streaming API
            if not tool_calls and tools and len(self.conversation) > 1:
                import sys
                print(f"[Engine] Streaming gave no tool calls, trying non-streaming fallback...", file=sys.stderr)
                try:
                    resp = await self.provider.chat(messages, tools=tools, max_tokens=max_tokens)
                    if resp and resp.choices:
                        for tc in resp.choices[0].get("message",{}).get("tool_calls",[]):
                            fn = tc.get("function", {})
                            args = fn.get("arguments", "{}")
                            if isinstance(args, str):
                                try: args = json.loads(args)
                                except: args = {}
                            tool_calls.append({"id": tc.get("id"), "name": fn.get("name",""), "arguments": args})
                except Exception as e:
                    print(f"[Engine] Non-streaming fallback failed: {e}", file=sys.stderr)
            if not tool_calls:
                self.conversation.append(ChatMessage(role="assistant", content=content_buffer))
                self._db.add_message(self.conversation_id, "assistant", content_buffer)
                yield {"type": "done", "content": content_buffer}
                self._is_running = False
                return

            assistant_msg = ChatMessage(role="assistant", content=None, tool_calls=[{"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": json.dumps(tc["arguments"])}} for tc in tool_calls])
            self.conversation.append(assistant_msg)

            call_count = 0
            for tc in tool_calls:
                if call_count >= 10:
                    break
                call_count += 1
                yield {"type": "tool_call", "name": tc["name"], "arguments": tc["arguments"]}
                tool = self.tool_registry.get(tc["name"])
                if tool:
                    # Check for empty or invalid arguments
                    args = tc.get("arguments", {})
                    if not args or not isinstance(args, dict) or len(args) == 0:
                        # Check if tool requires arguments
                        required = tool.parameters_schema.get("required", [])
                        if required:
                            missing = [p for p in required if p not in args]
                            result = {"error": f"Missing required arguments: {missing}", "hint": f"Expected: {required}"}
                        else:
                            result = {}
                    else:
                        try:
                            result = await tool.execute(**args)
                        except Exception as e:
                            result = {"error": str(e)}
                    yield {"type": "tool_result", "name": tc["name"], "result": result}
                    if isinstance(result, dict) and "error" not in result:
                        yield {"type": "text_delta", "content": f"[工具结果] {tc["name"]}: {str(result)[:200]}"}
                    self.conversation.append(ChatMessage(role="tool", content=json.dumps(result) if isinstance(result, dict) else str(result), tool_call_id=tc["id"]))

            if content_buffer:
                snapshot = self.context_mgr.get_snapshot(self.conversation)
                if snapshot.needs_compaction:
                    self.conversation = self.context_mgr.compact(self.conversation)

        yield {"type": "max_turns_exceeded"}
        self._is_running = False

    def _parse_tool_calls(self, text):
        results = []
        for match in re.finditer(r'<tool_call>\s*(\{.*?\})\s*</tool_call>', text, re.DOTALL):
            try:
                tc = json.loads(match.group(1))
                results.append({"id": f"call_{len(results)}", "name": tc.get("name",""), "arguments": tc.get("arguments",{})})
            except json.JSONDecodeError:
                pass
        return results

    def get_stats(self):
        return {"conversation_id": self.conversation_id, "messages": len(self.conversation), "tokens": self._total_tokens}
