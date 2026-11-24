from abc import ABC, abstractmethod
from typing import Any


class BaseAIProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Generate an AI response.

        Every provider must return the same normalized structure.
        """
        raise NotImplementedError

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider's name."""
        raise NotImplementedError