import logging
import math
import os
from typing import Any

try:
    import tiktoken  # type: ignore
except Exception:  # pragma: no cover
    tiktoken = None

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

        # Max input tokens for this embedding server/model (default 32k)
        self.max_input_tokens: int = int(
            os.getenv("OPENAI_EMBEDDING_MAX_INPUT_TOKENS")
            or config.extra_fields.get("max_input_tokens", 32000)
        )

        logger.info(
            f"Initialized OpenAILikeEmbeddingProvider base_url={self.base_url} model={self.base_model}"
        )

    def _get_embedding_kwargs(self, **kwargs):
        # Always omit `dimensions` for OpenAI-like embedding servers
        # Some servers/models (e.g., Qwen3-Embedding-4B) reject this param.
        model = kwargs.pop("model", None) or self.base_model
        embedding_kwargs: dict[str, Any] = {"model": model}
        # Copy all user kwargs except 'dimensions'
        for k, v in kwargs.items():
            if k == "dimensions":
                continue
            embedding_kwargs[k] = v
        return embedding_kwargs

    def _estimate_tokens(self, text: str) -> int:
        try:
            if tiktoken is not None:
                try:
                    enc = tiktoken.encoding_for_model(self.base_model)
                except Exception:
                    enc = tiktoken.get_encoding("cl100k_base")
                return len(enc.encode(text))
            # Fallback heuristic ~4 chars/token
            return max(1, int(len(text) / 4))
        except Exception:
            return len(text) // 4 or 1

    def _truncate_texts_to_limit(self, texts: list[str]) -> list[str]:
        """Ensure each input stays within the model's context window.

        Uses token estimation with tiktoken when available, otherwise a simple
        char-per-token heuristic. Truncates by characters conservatively.
        """
        if not texts:
            return texts
        truncated: list[str] = []
        char_per_token = 4
        char_limit = self.max_input_tokens * char_per_token
        for t in texts:
            try:
                tokens = self._estimate_tokens(t)
                if tokens > self.max_input_tokens:
                    # Conservative char-based truncation
                    truncated_text = t[:char_limit]
                    truncated.append(truncated_text)
                    logger.warning(
                        f"Embedding text truncated to ~{self.max_input_tokens} tokens (estimated {tokens})."
                    )
                else:
                    truncated.append(t)
            except Exception:
                truncated.append(t[:char_limit])
        return truncated

    async def _execute_task(self, task: dict[str, Any]) -> list[list[float]]:
        texts = task.get("texts")
        if texts is None:
            texts = [task["text"]]

        kwargs = self._get_embedding_kwargs(**task.get("kwargs", {}))

        try:
            # Truncate based on known 32k context window to avoid server errors
            texts = self._truncate_texts_to_limit(texts)
            # Ensure no stray 'dimensions' key is sent
            kwargs.pop("dimensions", None)
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
            # Truncate based on known 32k context window to avoid server errors
            texts = self._truncate_texts_to_limit(texts)
            # Ensure no stray 'dimensions' key is sent
            kwargs.pop("dimensions", None)
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

    async def async_get_embedding(
        self,
        text: str,
        stage: EmbeddingProvider.Step = EmbeddingProvider.Step.BASE,
        **kwargs,
    ) -> list[float]:
        if stage != EmbeddingProvider.Step.BASE:
            raise ValueError(
                "OpenAILikeEmbeddingProvider only supports search stage."
            )

        task = {
            "texts": [text],
            "stage": stage,
            "kwargs": kwargs,
        }
        result = await self._execute_with_backoff_async(task)
        return result[0]

    def get_embedding(
        self,
        text: str,
        stage: EmbeddingProvider.Step = EmbeddingProvider.Step.BASE,
        **kwargs,
    ) -> list[float]:
        if stage != EmbeddingProvider.Step.BASE:
            raise ValueError(
                "OpenAILikeEmbeddingProvider only supports search stage."
            )

        task = {
            "texts": [text],
            "stage": stage,
            "kwargs": kwargs,
        }
        result = self._execute_with_backoff_sync(task)
        return result[0]

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

