class ProviderError(Exception):
    """Base exception for AI provider errors."""


class InvalidAPIKeyError(ProviderError):
    """Raised when a provider API key is invalid."""


class ProviderTimeoutError(ProviderError):
    """Raised when a provider takes too long to respond."""


class ProviderRateLimitError(ProviderError):
    """Raised when a provider rate limit is reached."""


class ProviderResponseError(ProviderError):
    """Raised when a provider returns an unexpected response."""