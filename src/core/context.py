"""ContextManager - message window management, token-aware compaction strategies.

Equivalent to the Claude Code services/compact module and context management system.
"""

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class ContextConfig:
    max_tokens: int = 100000
    compaction_threshold: float = 0.75
    reserve_for_response: int = 4096
    keep_last_n_messages: int = 6


@dataclass
class ContextSnapshot:
    message_count: int
    estimated_tokens: int
    tool_calls_count: int
    needs_compaction: bool


class ContextManager:
    """Token-aware context window manager with compaction strategies.

    Strategies (from Claude Code MAP):
    - Summary compaction: summarize older messages, keep recent ones intact
    - Truncation: drop oldest messages beyond threshold
    - Hybrid: summarize middle messages, keep oldest system + newest user/assistant
    """

    def __init__(self, config=None, token_counter=None):
        self.config = config or ContextConfig()
        self._token_counter = token_counter or (lambda s: len(s) // 4)
        self._compacted_summaries = []
        self._compaction_count = 0

    def needs_compaction(self, messages, estimated_total_tokens):
        threshold = int(self.config.max_tokens * self.config.compaction_threshold)
        return estimated_total_tokens > threshold

    def compact(self, messages):
        """Apply compaction strategy and return reduced message list."""
        if len(messages) <= self.config.keep_last_n_messages:
            return messages

        system_msgs = [m for m in messages if self._get_role(m) == "system"]
        conv_msgs = [m for m in messages if self._get_role(m) != "system"]

        if len(conv_msgs) <= self.config.keep_last_n_messages:
            return messages

        recent = conv_msgs[-self.config.keep_last_n_messages:]
        older = conv_msgs[:-self.config.keep_last_n_messages]

        summary = self._summarize_messages(older)
        self._compacted_summaries.append(summary)
        self._compaction_count += 1

        compacted = list(system_msgs)
        for i, prev_summary in enumerate(self._compacted_summaries):
            compacted.append({
                "role": "system",
                "content": "<context_summary_" + str(i + 1) + ">\n" + prev_summary + "\n</context_summary_" + str(i + 1) + ">",
            })
        compacted.extend(recent)
        return compacted

    def _summarize_messages(self, messages):
        """Generate a concise summary of older messages."""
        parts = ["## Previous conversation summary"]
        for msg in messages:
            role = self._get_role(msg)
            content = self._get_content(msg)
            if content:
                short = content[:200].replace("\n", " ")
                parts.append("- [" + role + "]: " + short + "...")
            tool_calls = msg.get("tool_calls") if isinstance(msg, dict) else getattr(msg, "tool_calls", None)
            if tool_calls:
                for tc in tool_calls:
                    fn = tc.get("function", {}) if isinstance(tc, dict) else getattr(tc, "function", {})
                    parts.append("- [tool_call]: " + str(fn.get("name", "unknown") if isinstance(fn, dict) else "unknown"))
        return "\n".join(parts)

    def get_snapshot(self, messages):
        estimated = sum(self._token_counter(self._get_content(msg) or "") for msg in messages)
        tool_count = sum(1 for m in messages if self._has_tool_calls(m))
        return ContextSnapshot(
            message_count=len(messages),
            estimated_tokens=estimated,
            tool_calls_count=tool_count,
            needs_compaction=self.needs_compaction(messages, estimated),
        )

    @staticmethod
    def _get_role(msg):
        if isinstance(msg, dict):
            return msg.get("role", "unknown")
        return getattr(msg, "role", "unknown")

    @staticmethod
    def _get_content(msg):
        if isinstance(msg, dict):
            return msg.get("content", "")
        return getattr(msg, "content", "") or ""

    @staticmethod
    def _has_tool_calls(msg):
        if isinstance(msg, dict):
            return bool(msg.get("tool_calls"))
        return bool(getattr(msg, "tool_calls", None))
