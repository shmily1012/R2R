2025-09-04 21:42:56 - INFO - Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
2025-09-04 21:42:59 - ERROR - Async task execution failed: Bad Gateway
2025-09-04 21:42:59 - WARNING - Request failed (attempt 1): Bad Gateway
2025-09-04 21:43:01 - ERROR - Async task execution failed: Bad Gateway
2025-09-04 21:43:01 - WARNING - Request failed (attempt 2): Bad Gateway
2025-09-04 21:43:04 - ERROR - Async task execution failed: Bad Gateway
2025-09-04 21:43:04 - WARNING - Request failed (attempt 3): Bad Gateway
2025-09-04 21:43:04 - ERROR - Error in base endpoint completion() - Bad Gateway
Traceback (most recent call last):
  File "/app/core/main/api/v3/base_router.py", line 51, in wrapper
    func_result = await func(*args, **kwargs)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/core/main/api/v3/retrieval_router.py", line 882, in completion
    return await self.services.retrieval.completion(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/core/main/services/retrieval_service.py", line 970, in completion
    return await self.providers.llm.aget_completion(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/core/base/providers/llm.py", line 181, in aget_completion
    response = await self._execute_with_backoff_async(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/core/base/providers/llm.py", line 68, in _execute_with_backoff_async
    return await self._execute_task(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/core/providers/llm/openai.py", line 470, in _execute_task
    response = await client.chat.completions.create(**args)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/openai/resources/chat/completions/completions.py", line 2583, in create
    return await self._post(
           ^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/openai/_base_client.py", line 1794, in post
    return await self.request(cast_to, opts, stream=stream, stream_cls=stream_cls)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/openai/_base_client.py", line 1594, in request
    raise self._make_status_error_from_response(err.response) from None
openai.BadRequestError: Bad Gateway
2025-09-04 21:43:04 - ERROR - 172.25.0.1:60716 - "POST /v3/retrieval/completion HTTP/1.1" 500