2025-09-05 15:40:04 - INFO - LLM request payload: {"model": "llm", "stream": false, "max_tokens": 7629, "temperature": 0.7, "top_p": 0.8, "messages": [{"role": "system", "content": "You are a helpful agent."}, {"role": "user", "content": "## Task:\nYour task is to generate a descriptive summary of the document that follows. Your objective is to return a summary that is roughly 10% of the input document size while retaining as many key points as possible. Your response should begin with `The document contains `.\n### Document:\nDocument Title: CONTRIBUTING.md\nDocument Metadata: {\"version\": \"v0\"}\nDocument Text:\nR2R Contribution Guide\nQuick Start\n\nPre-Discussion: Feel free to propose your ideas via issues, Discord if you want to get early feedback.\nCode of Conduct: Adhere to our Code of Conduct in all interactions.\nPull Requests (PRs): Follow the PR process for contributions.\n\nPull Request Process\n\nDependencies: Ensure all dependencies are necessary and documented.\nDocumentation: Update README.md with any changes to interfaces, including new environment variables, exposed ports, and other relevant details.\nVersioning: Increment version numbers in examples and README.md following SemVer.\nReview: A PR can be merged after receiving approval from at least two other developers. If you lack merge permissions, request a review for merging.\n\nAttribution\nThis Code of Conduct adapts from the Contributor Covenant, version 1.4.\n\n### Query:\nReminder: Your task is to generate a descriptive summary of the document that was given. Your objective is to return a summary that is roughly 10% of the input document size while retaining as many key points as possible. Your response should begin with `The document contains `.\n## Response:\n"}]}

Provider List: https://docs.litellm.ai/docs/providers


Provider List: https://docs.litellm.ai/docs/providers

2025-09-05 15:40:06 - WARNING - Failed to truncate texts: This model isn't mapped yet. model=Qwen-Qwen3-Embedding-4B, custom_llm_provider=None. Add it here - https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json.

Provider List: https://docs.litellm.ai/docs/providers


Provider List: https://docs.litellm.ai/docs/providers

2025-09-05 15:40:07 - WARNING - Failed to truncate texts: This model isn't mapped yet. model=Qwen-Qwen3-Embedding-4B, custom_llm_provider=None. Add it here - https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json.
2025-09-05 15:40:07 - INFO - Successful ingestion for document_id: 15df7e62-584a-5257-ae77-91bf10d27028, with vector count: 1
2025-09-05 15:40:07 - WARNING - Automatic extraction not yet implemented for `simple` ingestion workflows.
2025-09-05 15:40:07 - INFO - 127.0.0.1:38290 - "POST /v3/documents HTTP/1.1" 202