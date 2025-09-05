2025-09-05 14:31:17 - ERROR - Async task execution failed: Error code: 400 - {'object': 'error', 'message': "This model's maximum context length is 131072 tokens. However, you requested 133475 tokens (13475 in the messages, 120000 in the completion). Please reduce the length of the messages or completion.", 'type': 'BadRequestError', 'param': None, 'code': 400}
2025-09-05 14:31:17 - WARNING - Request failed (attempt 3): Error code: 400 - {'object': 'error', 'message': "This model's maximum context length is 131072 tokens. However, you requested 133475 tokens (13475 in the messages, 120000 in the completion). Please reduce the length of the messages or completion.", 'type': 'BadRequestError', 'param': None, 'code': 400}
2025-09-05 14:31:17 - ERROR - Error in base endpoint create_document() - 500: Error during ingestion: Error code: 400 - {'object': 'error', 'message': "This model's maximum context length is 131072 tokens. However, you requested 133475 tokens (13475 in the messages, 120000 in the completion). Please reduce the length of the messages or completion.", 'type': 'BadRequestError', 'param': None, 'code': 400}
Traceback (most recent call last):
  File "/mnt/nvme1/workspace/R2R/py/core/main/orchestration/simple/ingestion_workflow.py", line 72, in ingest_files
    await service.augment_document_info(document_info, extractions)
  File "/mnt/nvme1/workspace/R2R/py/core/main/services/ingestion_service.py", line 309, in augment_document_info
    response = await self.providers.llm.aget_completion(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/nvme1/workspace/R2R/py/core/base/providers/llm.py", line 181, in aget_completion
    response = await self._execute_with_backoff_async(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/nvme1/workspace/R2R/py/core/base/providers/llm.py", line 68, in _execute_with_backoff_async
    return await self._execute_task(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/nvme1/workspace/R2R/py/core/providers/llm/openai.py", line 532, in _execute_task
    response = await client.chat.completions.create(**args)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/r2r/lib/python3.12/site-packages/openai/resources/chat/completions/completions.py", line 2583, in create
    return await self._post(
           ^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/r2r/lib/python3.12/site-packages/openai/_base_client.py", line 1794, in post
    return await self.request(cast_to, opts, stream=stream, stream_cls=stream_cls)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/r2r/lib/python3.12/site-packages/openai/_base_client.py", line 1594, in request
    raise self._make_status_error_from_response(err.response) from None
openai.BadRequestError: Error code: 400 - {'object': 'error', 'message': "This model's maximum context length is 131072 tokens. However, you requested 133475 tokens (13475 in the messages, 120000 in the completion). Please reduce the length of the messages or completion.", 'type': 'BadRequestError', 'param': None, 'code': 400}

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/mnt/nvme1/workspace/R2R/py/core/main/api/v3/base_router.py", line 51, in wrapper
    func_result = await func(*args, **kwargs)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/nvme1/workspace/R2R/py/core/main/api/v3/documents_router.py", line 572, in create_document
    await simple_ingestor["ingest-files"](workflow_input)
  File "/mnt/nvme1/workspace/R2R/py/core/main/orchestration/simple/ingestion_workflow.py", line 237, in ingest_files
    raise HTTPException(
fastapi.exceptions.HTTPException: 500: Error during ingestion: Error code: 400 - {'object': 'error', 'message': "This model's maximum context length is 131072 tokens. However, you requested 133475 tokens (13475 in the messages, 120000 in the completion). Please reduce the length of the messages or completion.", 'type': 'BadRequestError', 'param': None, 'code': 400}
2025-09-05 14:31:17 - ERROR - 127.0.0.1:47978 - "POST /v3/documents HTTP/1.1" 500