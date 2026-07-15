
"""LLMProvider ABC - Universal model provider abstraction layer."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator, Any


@dataclass
class ChatMessage:
    role: str
    content: str | list[dict]
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict] | None = None


@dataclass
class ChatResponse:
    id: str
    content: str
    finish_reason: str
    usage: dict
    model: str


@dataclass
class StreamEvent:
    type: str
    content: str = ""
    delta: str = ""
    done: bool = False
    usage: dict = field(default_factory=dict)
    tool_calls: list = field(default_factory=list)


class LLMProvider(ABC):
    provider_id: str = "generic"
    default_model: str = ""
    supports_prefix_cache: bool = False
    supports_tools: bool = True

    @abstractmethod
    async def chat(self, messages: list[ChatMessage],
                   model: str | None = None,
                   tools: list[dict] | None = None,
                   max_tokens: int = 4096,
                   temperature: float = 0.0) -> ChatResponse:
        ...

    @abstractmethod
    async def chat_stream(self, messages: list[ChatMessage],
                          model: str | None = None,
                          tools: list[dict] | None = None,
                          max_tokens: int = 4096,
                          temperature: float = 0.0) -> AsyncIterator[StreamEvent]:
        ...

    @abstractmethod
    def estimate_tokens(self, messages: list[ChatMessage]) -> int:
        ...

    async def health_check(self) -> bool:
        try:
            test_msg = ChatMessage(role="user", content="ping")
            resp = await self.chat([test_msg], max_tokens=1)
            return resp is not None
        except Exception:
            return False

    def supports_feature(self, feature: str) -> bool:
        features = {
            "streaming": True,
            "tools": self.supports_tools,
            "prefix_cache": self.supports_prefix_cache,
            "vision": False,
        }
        return features.get(feature, False)
