from app.providers.base import BaseAIProvider
from app.providers.openai import OpenAIProvider
from app.providers.gemini import GeminiProvider
from app.providers.exceptions import ProviderError


class ProviderRegistry:

    def __init__(self):
        self._providers: dict[str, BaseAIProvider] = {
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
        }

    def get_provider(self, name: str) -> BaseAIProvider:
        provider = self._providers.get(name.lower())

        if provider is None:
            raise ProviderError(
                f"Provider '{name}' is not supported."
            )

        return provider


provider_registry = ProviderRegistry()