import json
import os
import time
from collections.abc import Iterable
from typing import Any, AsyncGenerator, Optional
from uuid import UUID, uuid4

from fastapi import Body, Depends
from fastapi.responses import JSONResponse, StreamingResponse

from core.base import GenerationConfig, R2RException, SearchSettings

from .v3.base_router import BaseRouterV3


class OpenAIRouter(BaseRouterV3):
    """
    Provides a limited OpenAI-compatible surface so clients like OpenWebUI
    can integrate with the R2R services.
    """

    def _setup_routes(self) -> None:
        self._model_alias_map: dict[str, str] = {}
        self._alias_name = os.getenv("R2R_OPENAI_MODEL_ALIAS", "ddr4_rag")
        @self.router.get(
            "/models",
            dependencies=[Depends(self.rate_limit_dependency)],
        )
        async def list_models(
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ):
            catalog = self._collect_models()
            return {
                "object": "list",
                "data": catalog,
            }

        @self.router.get(
            "/models/{model_id}",
            dependencies=[Depends(self.rate_limit_dependency)],
        )
        async def get_model(
            model_id: str,
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ):
            catalog = {item["id"]: item for item in self._collect_models()}
            if model_id not in catalog:
                return self._error_response(
                    404, "Model not found", "model_not_found"
                )
            return catalog[model_id]

        @self.router.post(
            "/chat/completions",
            dependencies=[Depends(self.rate_limit_dependency)],
        )
        async def create_chat_completion(
            payload: dict[str, Any] = Body(...),
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ):
            try:
                messages = payload.get("messages")
                if not isinstance(messages, list) or not messages:
                    return self._error_response(
                        400, "`messages` must be a non-empty list."
                    )

                stream = bool(payload.get("stream", True))
                metadata = payload.get("metadata") or {}
                if not isinstance(metadata, dict):
                    metadata = {}

                query = metadata.get("query") or self._extract_user_query(messages)
                if not query:
                    return self._error_response(
                        400,
                        "Unable to determine the user query for retrieval-augmented completion.",
                    )

                model = self._resolve_model_id(
                    payload.get("model") or self._default_llm_model()
                )
                if not model:
                    return self._error_response(
                        400,
                        "No model provided and no default model is configured.",
                    )

                generation_config = self._build_generation_config(payload, model)
                generation_config.stream = False

                search_settings = self._extract_search_settings(metadata)
                include_web_search = self._coerce_bool(
                    metadata.get("include_web_search", False)
                )
                include_title_if_available = self._coerce_bool(
                    metadata.get("include_title_if_available", False)
                )
                task_prompt = metadata.get("task_prompt")

                rag_response = await self.services.retrieval.rag(
                    query=query,
                    search_settings=search_settings,
                    rag_generation_config=generation_config,
                    task_prompt=task_prompt,
                    include_title_if_available=include_title_if_available,
                    include_web_search=include_web_search,
                )

                if stream:
                    return await self._stream_rag_completion(rag_response, model)

                response_payload = self._build_rag_chat_completion(
                    rag_response, model
                )
                return JSONResponse(content=response_payload)

            except R2RException as exc:
                return self._error_response(
                    exc.status_code, exc.message, type(exc).__name__
                )
            except Exception as exc:  # pragma: no cover - unexpected runtime errors
                return self._error_response(
                    500, str(exc), type(exc).__name__ or "internal_error"
                )

        @self.router.post(
            "/embeddings",
            dependencies=[Depends(self.rate_limit_dependency)],
        )
        async def create_embeddings(
            payload: dict[str, Any] = Body(...),
            auth_user=Depends(self.providers.auth.auth_wrapper()),
        ):
            try:
                raw_input = payload.get("input")
                if raw_input is None:
                    return self._error_response(400, "`input` is required.")

                inputs = self._normalize_embedding_inputs(raw_input)
                model = payload.get("model") or self._default_embedding_model()
                if not model:
                    return self._error_response(
                        400,
                        "No model provided and no default embedding model is configured.",
                    )

                if (encoding_format := payload.get("encoding_format")) and (
                    encoding_format != "float"
                ):
                    return self._error_response(
                        400, "Only `float` encoding_format is supported."
                    )

                dimension = payload.get("dimensions")
                data = []
                for index, item in enumerate(inputs):
                    embedding = await self.services.retrieval.embedding(
                        text=item,
                        model=model,
                        dimension=dimension,
                    )
                    data.append(
                        {
                            "object": "embedding",
                            "index": index,
                            "embedding": embedding.results,
                        }
                    )

                return {
                    "object": "list",
                    "data": data,
                    "model": model,
                    "usage": {
                        "prompt_tokens": 0,
                        "total_tokens": 0,
                    },
                }

            except R2RException as exc:
                return self._error_response(
                    exc.status_code, exc.message, type(exc).__name__
                )
            except Exception as exc:  # pragma: no cover - unexpected runtime errors
                return self._error_response(
                    500, str(exc), type(exc).__name__ or "internal_error"
                )

    async def _stream_rag_completion(
        self,
        rag_response: Any,
        actual_model: str,
    ) -> StreamingResponse:
        answer = self._extract_answer(rag_response)
        alias_model = self._alias_from_actual(actual_model) or actual_model
        completion_id = self._generate_completion_id()
        created = int(time.time())
        usage = self._extract_usage(rag_response)
        rag_metadata = self._build_rag_metadata(rag_response)
        chunks = self._chunk_answer(answer)

        async def event_source() -> AsyncGenerator[str, None]:
            try:
                initial_payload = self._stream_payload(
                    completion_id,
                    created,
                    alias_model,
                    {"role": "assistant"},
                )
                yield f"data: {json.dumps(initial_payload, ensure_ascii=False)}\n\n"

                for piece in chunks:
                    payload = self._stream_payload(
                        completion_id,
                        created,
                        alias_model,
                        {"content": piece},
                    )
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

                final_payload = self._stream_payload(
                    completion_id,
                    created,
                    alias_model,
                    {},
                    finish_reason="stop",
                    usage=usage,
                    rag_metadata=rag_metadata,
                )
                yield f"data: {json.dumps(final_payload, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            except R2RException as exc:
                error_payload = {
                    "error": self._format_error(
                        exc.message, type(exc).__name__
                    )
                }
                yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as exc:  # pragma: no cover - unexpected runtime errors
                error_payload = {
                    "error": self._format_error(
                        str(exc), type(exc).__name__ or "internal_error"
                    )
                }
                yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_source(), media_type="text/event-stream"
        )

    def _collect_models(self) -> list[dict[str, Any]]:
        seen: dict[str, dict[str, Any]] = {}
        timestamp = int(time.time())

        def _add(model_id: Optional[str]) -> None:
            if model_id and model_id not in seen:
                seen[model_id] = {
                    "id": model_id,
                    "object": "model",
                    "created": timestamp,
                    "owned_by": "r2r",
                }

        completion_model = getattr(
            getattr(self.config.completion, "generation_config", None),
            "model",
            None,
        )
        _add(completion_model)

        app_config = getattr(self.config, "app", None)
        if app_config:
            for attr in (
                "quality_llm",
                "fast_llm",
                "vlm",
                "audio_lm",
                "reasoning_llm",
                "planning_llm",
            ):
                _add(getattr(app_config, attr, None))

        if not seen:
            _add("r2r-default-model")

        return self._alias_models(seen, timestamp)

    def _default_llm_model(self) -> Optional[str]:
        candidates = [
            getattr(
                getattr(self.config.completion, "generation_config", None),
                "model",
                None,
            ),
            getattr(self.config.app, "quality_llm", None),
            getattr(self.config.app, "fast_llm", None),
        ]
        return next((model for model in candidates if model), None)

    def _default_embedding_model(self) -> Optional[str]:
        candidates = [
            getattr(self.config.embedding, "base_model", None),
            getattr(self.config.completion_embedding, "base_model", None),
        ]
        return next((model for model in candidates if model), None)

    def _resolve_model_id(self, requested: Optional[str]) -> Optional[str]:
        default_model = self._default_llm_model()
        if requested is None or requested == "":
            return default_model

        if not self._model_alias_map:
            self._collect_models()

        if requested in self._model_alias_map:
            return self._model_alias_map[requested]

        if requested == self._alias_name and default_model:
            self._model_alias_map[requested] = default_model
            return default_model

        return requested

    def _alias_models(
        self, seen: dict[str, dict[str, Any]], timestamp: int
    ) -> list[dict[str, Any]]:
        self._model_alias_map.clear()
        default_model = self._default_llm_model()
        preferred_alias = (
            self._alias_name if self._alias_name else default_model
        )

        results: list[dict[str, Any]] = []
        for actual_id, metadata in seen.items():
            alias_id = (
                preferred_alias if actual_id == default_model else actual_id
            )

            if alias_id in self._model_alias_map:
                continue

            self._model_alias_map[alias_id] = actual_id
            entry = dict(metadata)
            entry["id"] = alias_id
            entry["created"] = metadata.get("created", timestamp)
            results.append(entry)

        return results

    def _alias_from_actual(self, actual: Optional[str]) -> Optional[str]:
        if actual is None or actual == "":
            return None
        if not self._model_alias_map:
            self._collect_models()
        for alias, target in self._model_alias_map.items():
            if target == actual:
                return alias
        return None

    def _to_serializable(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: self._to_serializable(val) for key, val in value.items()
            }
        if isinstance(value, (list, tuple, set)):
            return [self._to_serializable(item) for item in value]
        if isinstance(value, UUID):
            return str(value)
        if hasattr(value, "model_dump"):
            return self._to_serializable(value.model_dump())
        if hasattr(value, "to_dict"):
            return self._to_serializable(value.to_dict())
        if hasattr(value, "as_dict"):
            return self._to_serializable(value.as_dict())
        return value

    def _extract_user_query(self, messages: list[Any]) -> Optional[str]:
        for message in reversed(messages):
            if not isinstance(message, dict):
                continue
            if message.get("role") != "user":
                continue
            content = message.get("content")
            flattened = self._flatten_message_content(content)
            if flattened:
                return flattened.strip()
        return None

    def _flatten_message_content(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        value = (
                            item.get("text")
                            or item.get("value")
                            or item.get("content")
                        )
                        if value:
                            parts.append(str(value))
                    elif "content" in item:
                        parts.append(str(item["content"]))
                elif isinstance(item, str):
                    parts.append(item)
            return "".join(parts)
        if content is not None:
            return str(content)
        return ""

    def _coerce_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes", "y", "on"}
        if isinstance(value, (int, float)):
            return value != 0
        return bool(value)

    def _extract_search_settings(
        self, metadata: dict[str, Any]
    ) -> SearchSettings:
        candidate = metadata.get("search_settings")
        if isinstance(candidate, dict):
            try:
                return SearchSettings(**candidate)
            except Exception:
                pass
        return SearchSettings()

    def _extract_answer(self, rag_response: Any) -> str:
        answer = getattr(rag_response, "generated_answer", None)
        if not answer:
            answer = getattr(rag_response, "completion", None)
        return answer or ""

    def _extract_usage(self, rag_response: Any) -> dict[str, int]:
        metadata = getattr(rag_response, "metadata", {}) or {}
        usage = metadata.get("usage") if isinstance(metadata, dict) else None
        result = {}
        if isinstance(usage, dict):
            for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
                value = usage.get(key)
                if isinstance(value, int):
                    result[key] = value
        if result:
            return result
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _build_rag_metadata(self, rag_response: Any) -> dict[str, Any]:
        extra: dict[str, Any] = {}
        citations = getattr(rag_response, "citations", None)
        if citations:
            extra["citations"] = [
                citation.as_dict()
                if hasattr(citation, "as_dict")
                else citation.dict()
                for citation in citations
            ]
        search_results = getattr(rag_response, "search_results", None)
        if search_results:
            try:
                extra["search_results"] = search_results.as_dict()
            except AttributeError:
                try:
                    extra["search_results"] = search_results.to_dict()
                except AttributeError:
                    extra["search_results"] = search_results
        metadata = getattr(rag_response, "metadata", None)
        if metadata:
            extra["metadata"] = metadata
        return self._to_serializable(extra)

    def _chunk_answer(self, text: str, chunk_size: int = 256) -> list[str]:
        if not text:
            return []
        return [
            text[i : i + chunk_size] for i in range(0, len(text), chunk_size)
        ]

    def _stream_payload(
        self,
        completion_id: str,
        created: int,
        model: str,
        delta: dict[str, Any],
        finish_reason: Optional[str] = None,
        usage: Optional[dict[str, Any]] = None,
        rag_metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        choice: dict[str, Any] = {
            "index": 0,
            "delta": delta,
            "finish_reason": finish_reason,
        }
        payload: dict[str, Any] = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [choice],
        }
        if usage is not None:
            payload["usage"] = usage
        if rag_metadata and finish_reason:
            payload["rag"] = rag_metadata
        return self._to_serializable(payload)

    def _generate_completion_id(self) -> str:
        return f"chatcmpl-{uuid4().hex}"

    def _build_rag_chat_completion(
        self,
        rag_response: Any,
        actual_model: str,
    ) -> dict[str, Any]:
        alias_model = self._alias_from_actual(actual_model) or actual_model
        answer = self._extract_answer(rag_response)
        usage = self._extract_usage(rag_response)
        rag_metadata = self._build_rag_metadata(rag_response)
        payload = {
            "id": self._generate_completion_id(),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": alias_model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": answer,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": usage,
        }
        if rag_metadata:
            payload["rag"] = rag_metadata
        return self._to_serializable(payload)

    def _build_generation_config(
        self, payload: dict[str, Any], model: str
    ) -> GenerationConfig:
        gen_kwargs: dict[str, Any] = {
            "model": model,
            "temperature": payload.get("temperature"),
            "top_p": payload.get("top_p"),
            "stream": payload.get("stream", False),
            "max_tokens": payload.get("max_tokens")
            or payload.get("max_completion_tokens"),
            "response_format": payload.get("response_format"),
            "tools": payload.get("tools"),
            "functions": payload.get("functions"),
        }

        add_generation_kwargs = payload.get("add_generation_kwargs") or {}
        if add_generation_kwargs:
            gen_kwargs["add_generation_kwargs"] = add_generation_kwargs

        cleaned = {k: v for k, v in gen_kwargs.items() if v is not None}
        return GenerationConfig(**cleaned)

    def _normalize_embedding_inputs(
        self, raw_input: Any
    ) -> list[str]:
        if isinstance(raw_input, str):
            return [raw_input]
        if isinstance(raw_input, (list, tuple)):
            normalized: list[str] = []
            for element in raw_input:
                if isinstance(element, str):
                    normalized.append(element)
                elif isinstance(element, Iterable):
                    normalized.append(" ".join(map(str, element)))
                else:
                    normalized.append(str(element))
            return normalized
        return [str(raw_input)]

    @staticmethod
    def _format_error(message: str, error_type: str) -> dict[str, Any]:
        return {
            "message": message,
            "type": error_type,
            "param": None,
            "code": None,
        }

    @staticmethod
    def _error_response(
        status_code: int, message: str, error_type: str = "invalid_request_error"
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"error": OpenAIRouter._format_error(message, error_type)},
        )
