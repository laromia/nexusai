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


class GeminiProvider(BaseAIProvider):

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.default_model = settings.GEMINI_MODEL
        self.timeout = settings.PROVIDER_TIMEOUT

    def get_provider_name(self) -> str:
        return "gemini"

    async def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any
    ) -> dict[str, Any]:

        if not self.api_key:
            raise InvalidAPIKeyError(
                "Gemini API key is not configured."
            )

        model = kwargs.get("model") or self.default_model
        max_output_tokens = kwargs.get("max_output_tokens", 512)

        system_messages = [
            message["content"]
            for message in messages
            if message["role"] == "system"
        ]

        conversation = [
            {
                "role": (
                    "model"
                    if message["role"] == "assistant"
                    else "user"
                ),
                "parts": [{"text": message["content"]}]
            }
            for message in messages
            if message["role"] != "system"
        ]

        payload = {
            "contents": conversation,
            "generationConfig": {
                "maxOutputTokens": max_output_tokens
            }
        }

        if system_messages:
            payload["systemInstruction"] = {
                "parts": [
                    {"text": "\n".join(system_messages)}
                ]
            }

        url = f"{self.BASE_URL}/{model}:generateContent"

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                response = await client.post(
                    url,
                    params={"key": self.api_key},
                    json=payload
                )

                if response.status_code == 401:
                    raise InvalidAPIKeyError(
                        "Gemini rejected the API key."
                    )

                if response.status_code == 403:
                    raise ProviderError(
                        "Gemini access denied. Check API key permissions."
                    )

                if response.status_code == 400:
                    raise ProviderResponseError(
                        "Gemini rejected the request parameters."
                    )

                if response.status_code == 429:
                    raise ProviderRateLimitError(
                        "Gemini rate limit reached."
                    )

                response.raise_for_status()
                data = response.json()

        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(
                "Gemini request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                f"Gemini HTTP error: {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            raise ProviderError(
                "Could not connect to Gemini."
            ) from exc

        try:
            candidates = data.get("candidates", [])

            if not candidates:
                raise ProviderResponseError(
                    "Gemini returned no response candidates."
                )

            content = "".join(
                part.get("text", "")
                for part in candidates[0]["content"]["parts"]
            )

            usage_data = data.get("usageMetadata", {})

            return {
                "provider": "gemini",
                "model": model,
                "content": content,
                "usage": {
                    "prompt_tokens": usage_data.get(
                        "promptTokenCount", 0
                    ),
                    "completion_tokens": usage_data.get(
                        "candidatesTokenCount", 0
                    ),
                    "total_tokens": usage_data.get(
                        "totalTokenCount", 0
                    ),
                }
            }

        except (KeyError, TypeError) as exc:
            raise ProviderResponseError(
                "Unexpected response format from Gemini."
            ) from exc
