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

        Every provider must implement this method.
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Return the provider's name.
        """
        pass