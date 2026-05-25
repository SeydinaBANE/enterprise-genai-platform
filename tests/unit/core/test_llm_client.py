from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from src.core.config import settings
from src.core.llm_client import LLMClient
from src.core.models import Message


def _mock_completion(content: str = "Hello!") -> MagicMock:
    resp = MagicMock()
    resp.choices[0].message.content = content
    resp.choices[0].finish_reason = "stop"
    resp.usage.prompt_tokens = 10
    resp.usage.completion_tokens = 5
    return resp


async def test_complete_returns_llm_response() -> None:
    with patch("litellm.acompletion", new_callable=AsyncMock, return_value=_mock_completion()):
        client = LLMClient()
        result = await client.complete([Message(role="user", content="Hi")])

    assert result.content == "Hello!"
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 5
    assert result.finish_reason == "stop"


async def test_complete_with_custom_model() -> None:
    mock_resp = _mock_completion("Custom model response")
    with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_resp) as mock_call:
        client = LLMClient()
        await client.complete([Message(role="user", content="Hi")], model="gpt-4o")

    call_kwargs = mock_call.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o"


async def test_embed_returns_embeddings() -> None:
    mock_resp = MagicMock()
    mock_resp.data = [{"embedding": [0.1, 0.2, 0.3]}]

    with patch("litellm.aembedding", new_callable=AsyncMock, return_value=mock_resp):
        client = LLMClient()
        result = await client.embed(["hello"])

    assert result == [[0.1, 0.2, 0.3]]


async def test_embed_multiple_texts() -> None:
    mock_resp = MagicMock()
    mock_resp.data = [{"embedding": [0.1]}, {"embedding": [0.2]}]

    with patch("litellm.aembedding", new_callable=AsyncMock, return_value=mock_resp):
        client = LLMClient()
        result = await client.embed(["a", "b"])

    assert len(result) == 2


def test_default_model_from_settings() -> None:
    client = LLMClient()
    assert client._model == settings.llm_model


def test_custom_default_model() -> None:
    client = LLMClient(default_model="my-model")
    assert client._model == "my-model"
