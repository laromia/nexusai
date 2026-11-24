import httpx

from typing import Any

from app.core.config import settings
from app.providers.base import BaseAIProvider
from app.providers.exceptions import (
    InvalidAPIKeyError,
    ProviderError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
)


class OpenAIProvider(BaseAIProvider):

    BASE_URL = "https://api.openai.com/v1/responses"

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.default_model = settings.OPENAI_MODEL
        self.timeout = settings.PROVIDER_TIMEOUT

    def get_provider_name(self) -> str:
        return "openai"

    async def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any
    ) -> dict[str, Any]:

        if not self.api_key:
            raise InvalidAPIKeyError(
                "OpenAI API key is not configured."
            )

        model = kwargs.get("model") or self.default_model
        max_output_tokens = kwargs.get("max_output_tokens", 512)

        # Separate system instructions from conversation messages.
        system_messages = [
            message["content"]
            for message in messages
            if message["role"] == "system"
        ]

        conversation = [
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in messages
            if message["role"] != "system"
        ]

        payload = {
            "model": model,
            "input": conversation,
            "max_output_tokens": max_output_tokens,
        }

        if system_messages:
            payload["instructions"] = "\n".join(system_messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload
                )

                if response.status_code == 401:
                    raise InvalidAPIKeyError(
                        "OpenAI rejected the API key."
                    )

                if response.status_code == 429:
                    raise ProviderRateLimitError(
                        "OpenAI rate limit reached."
                    )

                response.raise_for_status()

                data = response.json()

        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(
                "OpenAI request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                f"OpenAI HTTP error: {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            raise ProviderError(
                "Could not connect to OpenAI."
            ) from exc

        try:
            content = "".join(
                part["text"]
                for item in data["output"]
                if item.get("type") == "message"
                for part in item.get("content", [])
                if part.get("type") == "output_text"
            )

            usage_data = data.get("usage") or {}

            return {
                "provider": "openai",
                "model": data.get("model", model),
                "content": content,
                "usage": {
                    "prompt_tokens": usage_data.get("input_tokens", 0),
                    "completion_tokens": usage_data.get("output_tokens", 0),
                    "total_tokens": usage_data.get("total_tokens", 0),
                }
            }

        except (KeyError, TypeError) as exc:
            raise ProviderResponseError(
                "Unexpected response format from OpenAI."
            ) from exc