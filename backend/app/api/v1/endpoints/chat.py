from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse, TokenUsage
from app.providers.registry import provider_registry
from app.providers.exceptions import (
    InvalidAPIKeyError,
    ProviderError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        provider = provider_registry.get_provider(request.provider)

        result = await provider.generate(
            messages=[
                message.model_dump()
                for message in request.messages
            ],
            model=request.model,
            max_output_tokens=request.max_output_tokens
        )

        return ChatResponse(
            provider=result["provider"],
            model=result["model"],
            content=result["content"],
            usage=TokenUsage(**result["usage"])
        )

    except InvalidAPIKeyError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    except ProviderRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc

    except ProviderTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc

    except ProviderResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
