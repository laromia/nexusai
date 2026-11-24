from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    provider: Literal["openai", "gemini"]
    model: str | None = None

    messages: list[ChatMessage] = Field(min_length=1)

    max_output_tokens: int = Field(
        default=512,
        ge=1,
        le=8192
    )


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    provider: str
    model: str
    content: str
    usage: TokenUsage