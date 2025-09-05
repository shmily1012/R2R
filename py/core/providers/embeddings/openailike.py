import logging
import math
import os
from typing import Any

from openai import AsyncOpenAI, OpenAI

from core.base import (
    ChunkSearchResult,
    EmbeddingConfig,
    EmbeddingProvider,
)

from .utils import truncate_texts_to_token_limit

logger = logging.getLogger()


class OpenAILikeEmbeddingProvider(EmbeddingProvider):
    """
    Flexible OpenAI-compatible embedding provider for local/self-hosted servers.

    Differences vs OpenAIEmbeddingProvider:
    - No strict model name or dimension validation.
    - Accepts custom base/key via OPENAI_API_LIKE_BASE and OPENAI_API_LIKE_KEY.
    - Falls back to OPENAI_API_BASE/OPENAI_API_KEY or LMSTUDIO_API_BASE/LMSTUDIO_API_KEY.
    - Uses a dummy API key if none is provided.
    """

    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)

        base_url = (
            os.getenv("OPENAI_API_LIKE_BASE")
            or os.getenv("OPENAI_API_BASE")
            or os.getenv("LMSTUDIO_API_BASE")
            or "http://localhost:8000/v1"
        )
        api_key = (
            os.getenv("OPENAI_API_LIKE_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("LMSTUDIO_API_KEY")
            or "dummy"
        )

        self.base_url = base_url
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

        # Do not enforce a specific model; use provided base_model or a generic value
        self.base_model = config.base_model or "embedding"
        self.base_dimension = config.base_dimension

        logger.info(
            f"Initialized OpenAILikeEmbeddingProvider base_url={self.base_url} model={self.base_model}"
        )

    def _get_embedding_kwargs(self, **kwargs):
        # Keep user overrides and drop NaN dimensions
        model = kwargs.pop("model", None) or self.base_model
        dims = kwargs.pop("dimensions", self.base_dimension)
        if isinstance(dims, float) and math.isnan(dims):
            dims = None
        embedding_kwargs: dict[str, Any] = {"model": model}
        if dims is not None:
            embedding_kwargs["dimensions"] = dims
        embedding_kwargs.update(kwargs)
        return embedding_kwargs

    async def _execute_task(self, task: dict[str, Any]) -> list[list[float]]:
        texts = task.get("texts")
        if texts is None:
            texts = [task["text"]]

        kwargs = self._get_embedding_kwargs(**task.get("kwargs", {}))

        try:
            # Best-effort truncation if server enforces token limits
            if kwargs.get("model"):
                try:
                    texts = truncate_texts_to_token_limit(texts, kwargs["model"])
                except Exception:
                    pass

            response = await self.async_client.embeddings.create(
                input=texts, **kwargs
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            # Some OpenAI-compatible servers (e.g., Qwen embeddings) do not
            # support the `dimensions`/matryoshka parameter at all. If the
            # error indicates this, retry once without `dimensions`.
            message = str(e)
            should_retry_without_dims = (
                ("matryoshka" in message.lower() or "dimensions" in message.lower())
                and isinstance(kwargs, dict)
                and "dimensions" in kwargs
            )

            if should_retry_without_dims:
                try:
                    retry_kwargs = dict(kwargs)
                    retry_kwargs.pop("dimensions", None)
                    logger.warning(
                        "Embedding server rejected `dimensions`; retrying without it. model=%s",
                        retry_kwargs.get("model"),
                    )
                    response = await self.async_client.embeddings.create(
                        input=texts, **retry_kwargs
                    )
                    return [data.embedding for data in response.data]
                except Exception as e2:
                    error_msg = f"Error getting embeddings (async): {str(e2)}"
                    logger.error(error_msg)
                    raise ValueError(error_msg) from e2

            error_msg = f"Error getting embeddings (async): {message}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

    def _execute_task_sync(self, task: dict[str, Any]) -> list[list[float]]:
        texts = task.get("texts")
        if texts is None:
            texts = [task["text"]]

        kwargs = self._get_embedding_kwargs(**task.get("kwargs", {}))

        try:
            if kwargs.get("model"):
                try:
                    texts = truncate_texts_to_token_limit(texts, kwargs["model"])
                except Exception:
                    pass

            response = self.client.embeddings.create(input=texts, **kwargs)
            return [data.embedding for data in response.data]
        except Exception as e:
            message = str(e)
            should_retry_without_dims = (
                ("matryoshka" in message.lower() or "dimensions" in message.lower())
                and isinstance(kwargs, dict)
                and "dimensions" in kwargs
            )

            if should_retry_without_dims:
                try:
                    retry_kwargs = dict(kwargs)
                    retry_kwargs.pop("dimensions", None)
                    logger.warning(
                        "Embedding server rejected `dimensions`; retrying without it. model=%s",
                        retry_kwargs.get("model"),
                    )
                    response = self.client.embeddings.create(
                        input=texts, **retry_kwargs
                    )
                    return [data.embedding for data in response.data]
                except Exception as e2:
                    error_msg = f"Error getting embeddings: {str(e2)}"
                    logger.error(error_msg)
                    raise ValueError(error_msg) from e2

            error_msg = f"Error getting embeddings: {message}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

    def rerank(
        self,
        query: str,
        results: list[ChunkSearchResult],
        stage: EmbeddingProvider.Step = EmbeddingProvider.Step.RERANK,
        limit: int = 10,
    ):
        return results[:limit]

    async def arerank(
        self,
        query: str,
        results: list[ChunkSearchResult],
        stage: EmbeddingProvider.Step = EmbeddingProvider.Step.RERANK,
        limit: int = 10,
    ):
        return results[:limit]

