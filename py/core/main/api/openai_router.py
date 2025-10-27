import json
import os
import time
from collections.abc import Iterable
from typing import Any, AsyncGenerator, Optional

from fastapi import Body, Depends
from fastapi.responses import JSONResponse, StreamingResponse

from core.base import GenerationConfig, Message, R2RException

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

                model = self._resolve_model_id(payload.get("model"))
                if not model:
                    return self._error_response(
                        400,
                        "No model provided and no default model is configured.",
                    )

                stream = bool(payload.get("stream", False))
                generation_config = self._build_generation_config(payload, model)
                message_objects = [Message(**message) for message in messages]
                extra_kwargs = self._completion_extra_kwargs(payload)

                if stream:
                    return await self._stream_chat_completion(
                        message_objects, generation_config, extra_kwargs
                    )

                completion = await self.services.retrieval.completion(
                    messages=message_objects,
                    generation_config=generation_config,
                    **extra_kwargs,
                )
                response_payload = completion.results.model_dump(
                    exclude_none=True
                )
                alias_model = self._alias_from_actual(
                    response_payload.get("model")
                )
                if alias_model:
                    response_payload["model"] = alias_model
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

    async def _stream_chat_completion(
        self,
        messages: list[Message],
        generation_config: GenerationConfig,
        extra_kwargs: dict[str, Any],
    ) -> StreamingResponse:
        async def event_source() -> AsyncGenerator[str, None]:
            try:
                stream = self.providers.llm.aget_completion_stream(
                    messages=[message.to_dict() for message in messages],
                    generation_config=generation_config,
                    **extra_kwargs,
                )

                async for chunk in stream:
                    payload = chunk.model_dump(exclude_none=True)
                    alias_model = self._alias_from_actual(payload.get("model"))
                    if alias_model:
                        payload["model"] = alias_model
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

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

    def _completion_extra_kwargs(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        allowed_keys = {
            "frequency_penalty",
            "presence_penalty",
            "logit_bias",
            "stop",
            "n",
            "user",
            "function_call",
            "tool_choice",
            "metadata",
            "parallel_tool_calls",
            "seed",
            "stream_options",
            "service_tier",
            "top_logprobs",
            "logprobs",
        }
        return {k: payload[k] for k in allowed_keys if k in payload}

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
