import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.chat import provider_registry
from app.providers.exceptions import (
    InvalidAPIKeyError,
    ProviderTimeoutError,
)


client = TestClient(app)


class FakeProvider:

    def __init__(self, name):
        self.name = name

    def get_provider_name(self):
        return self.name

    async def generate(self, messages, **kwargs):
        return {
            "provider": self.name,
            "model": "test-model",
            "content": "This is a test response.",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 8,
                "total_tokens": 18,
            }
        }


@pytest.mark.parametrize("provider_name", ["openai", "gemini"])
def test_chat_success(provider_name, monkeypatch):

    monkeypatch.setattr(
        provider_registry,
        "get_provider",
        lambda name: FakeProvider(name)
    )

    response = client.post(
        "/api/v1/chat/",
        json={
            "provider": provider_name,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello NexusAI!"
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["provider"] == provider_name
    assert data["content"] == "This is a test response."
    assert data["usage"]["total_tokens"] == 18


def test_chat_invalid_api_key(monkeypatch):

    class InvalidProvider:

        async def generate(self, messages, **kwargs):
            raise InvalidAPIKeyError("Invalid test key.")

    monkeypatch.setattr(
        provider_registry,
        "get_provider",
        lambda name: InvalidProvider()
    )

    response = client.post(
        "/api/v1/chat/",
        json={
            "provider": "openai",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello!"
                }
            ]
        }
    )

    assert response.status_code == 401


def test_chat_timeout(monkeypatch):

    class TimeoutProvider:

        async def generate(self, messages, **kwargs):
            raise ProviderTimeoutError("Test timeout.")

    monkeypatch.setattr(
        provider_registry,
        "get_provider",
        lambda name: TimeoutProvider()
    )

    response = client.post(
        "/api/v1/chat/",
        json={
            "provider": "gemini",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello!"
                }
            ]
        }
    )

    assert response.status_code == 504


def test_chat_validation_error():

    response = client.post(
        "/api/v1/chat/",
        json={
            "provider": "openai",
            "messages": []
        }
    )

    assert response.status_code == 422