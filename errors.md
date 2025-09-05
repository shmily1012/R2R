2025-09-05 10:26:21 - WARNING - Skipping data after last boundary
2025-09-05 10:26:21 - INFO - Initializing text splitter with method: ChunkingStrategy.RECURSIVE
2025-09-05 10:26:21 - INFO - LLM request target: provider=lmstudio base_url=http://localhost:8000/v1 model=llm api_key=123
2025-09-05 10:26:21 - INFO - LLM request payload: {"model": "llm", "stream": false, "max_tokens": 12000, "temperature": 0.7, "top_p": 0.8, "messages": [{"role": "system", "content": "You are a helpful agent."}, {"role": "user", "content": "## Task:\nYour task is to generate a descriptive summary of the document that follows. Your objective is to return a summary that is roughly 10% of the input document size while retaining as many key points as possible. Your response should begin with `The document contains `.\n### Document:\nDocument Title: sample_doc.txt\nDocument Metadata: {\"version\": \"v0\"}\nDocument Text:\nDeepSeek R1 is a reasoning model. This file is a simple demo.\nRAG combines retrieval with generation to produce grounded answers.\n\n### Query:\nReminder: Your task is to generate a descriptive summary of the document that was given. Your objective is to return a summary that is roughly 10% of the input document size while retaining as many key points as possible. Your response should begin with `The document contains `.\n## Response:\n"}]}

Provider List: https://docs.litellm.ai/docs/providers


Provider List: https://docs.litellm.ai/docs/providers

2025-09-05 10:26:22 - WARNING - Failed to truncate texts: This model isn't mapped yet. model=Qwen-Qwen3-Embedding-4B, custom_llm_provider=None. Add it here - https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json.
2025-09-05 10:26:22 - ERROR - Error getting embeddings (async): Error code: 400 - {'object': 'error', 'message': 'Model "Qwen-Qwen3-Embedding-4B" does not support matryoshka representation, changing output dimensions will lead to poor results.', 'type': 'BadRequestError', 'param': None, 'code': 400}
2025-09-05 10:26:22 - WARNING - Request failed (attempt 1): Error getting embeddings (async): Error code: 400 - {'object': 'error', 'message': 'Model "Qwen-Qwen3-Embedding-4B" does not support matryoshka representation, changing output dimensions will lead to poor results.', 'type': 'BadRequestError', 'param': None, 'code': 400}

Provider List: https://docs.litellm.ai/docs/providers


Provider List: https://docs.litellm.ai/docs/providers

2025-09-05 10:26:23 - WARNING - Failed to truncate texts: This model isn't mapped yet. model=Qwen-Qwen3-Embedding-4B, custom_llm_provider=None. Add it here - https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json.
2025-09-05 10:26:23 - ERROR - Error getting embeddings (async): Error code: 400 - {'object': 'error', 'message': 'Model "Qwen-Qwen3-Embedding-4B" does not support matryoshka representation, changing output dimensions will lead to poor results.', 'type': 'BadRequestError', 'param': None, 'code': 400}
2025-09-05 10:26:23 - WARNING - Request failed (attempt 2): Error getting embeddings (async): Error code: 400 - {'object': 'error', 'message': 'Model "Qwen-Qwen3-Embedding-4B" does not support matryoshka representation, changing output dimensions will lead to poor results.', 'type': 'BadRequestError', 'param': None, 'code': 400}

Provider List: https://docs.litellm.ai/docs/providers


Provider List: https://docs.litellm.ai/docs/providers

2025-09-05 10:26:23 - WARNING - Failed to truncate texts: This model isn't mapped yet. model=Qwen-Qwen3-Embedding-4B, custom_llm_provider=None. Add it here - https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json.
2025-09-05 10:26:23 - ERROR - Error getting embeddings (async): Error code: 400 - {'object': 'error', 'message': 'Model "Qwen-Qwen3-Embedding-4B" does not support matryoshka representation, changing output dimensions will lead to poor results.', 'type': 'BadRequestError', 'param': None, 'code': 400}
2025-09-05 10:26:23 - WARNING - Request failed (attempt 3): Error getting embeddings (async): Error code: 400 - {'object': 'error', 'message': 'Model "Qwen-Qwen3-Embedding-4B" does not support matryoshka representation, changing output dimensions will lead to poor results.', 'type': 'BadRequestError', 'param': None, 'code': 400}
2025-09-05 10:26:23 - ERROR - Error running orchestrated ingestion: 500: Error during ingestion: Error getting embeddings (async): Error code: 400 - {'object': 'error', 'message': 'Model "Qwen-Qwen3-Embedding-4B" does not support matryoshka representation, changing output dimensions will lead to poor results.', 'type': 'BadRequestError', 'param': None, 'code': 400} 

Attempting to run without orchestration.