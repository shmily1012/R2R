2025-09-05 10:12:07 - INFO - R2RIngestionProvider initialized with config: app=AppConfig(extra_fields={}, project_name='r2r_local', user_tools_path=None, default_max_documents_per_user=10000, default_max_chunks_per_user=10000000, default_max_collections_per_user=5000, default_max_upload_size=214748364800, quality_llm='lmstudio/llm', fast_llm='lmstudio/llm', vlm='lmstudio/llm', audio_lm='openai/whisper-1', reasoning_llm='lmstudio/llm', planning_llm='lmstudio/llm', max_upload_size_by_type={'txt': 2000000, 'md': 2000000, 'tsv': 2000000, 'csv': 5000000, 'html': 5000000, 'doc': 10000000, 'docx': 10000000, 'ppt': 20000000, 'pptx': 20000000, 'xls': 10000000, 'xlsx': 10000000, 'odt': 5000000, 'pdf': 30000000, 'eml': 5000000, 'msg': 5000000, 'p7s': 5000000, 'bmp': 5000000, 'heic': 5000000, 'jpeg': 5000000, 'jpg': 5000000, 'png': 5000000, 'tiff': 5000000, 'epub': 10000000, 'rtf': 5000000, 'rst': 5000000, 'org': 5000000}) extra_fields={} provider='r2r' excluded_parsers=[] chunking_strategy=<ChunkingStrategy.RECURSIVE: 'recursive'> chunk_size=1024 chunk_overlap=512 chunk_enrichment_settings=ChunkEnrichmentSettings(enable_chunk_enrichment=False, n_chunks=2, generation_config=None, chunk_enrichment_prompt='chunk_enrichment') extra_parsers={'pdf': ['zerox', 'ocr']} audio_transcription_model=None vlm=None vlm_batch_size=20 vlm_max_tokens_to_sample=1024 max_concurrent_vlm_tasks=20 vlm_ocr_one_page_per_chunk=True skip_document_summary=False document_summary_system_prompt='system' document_summary_task_prompt='summary' chunks_for_document_summary=128 document_summary_model='lmstudio/llm' parser_overrides={} automatic_extraction=True document_summary_max_length=100000 separator=None
2025-09-05 10:12:07 - INFO - Default admin user already exists.
2025-09-05 10:12:07 - ERROR - Error 3 validation errors for R2RProviders
embedding.is-instance[LiteLLMEmbeddingProvider]
  Input should be an instance of LiteLLMEmbeddingProvider [type=is_instance_of, input_value=<core.providers.embedding...bject at 0x7f6f8cff0f50>, input_type=OpenAILikeEmbeddingProvider]
    For further information visit https://errors.pydantic.dev/2.11/v/is_instance_of
embedding.is-instance[OpenAIEmbeddingProvider]
  Input should be an instance of OpenAIEmbeddingProvider [type=is_instance_of, input_value=<core.providers.embedding...bject at 0x7f6f8cff0f50>, input_type=OpenAILikeEmbeddingProvider]
    For further information visit https://errors.pydantic.dev/2.11/v/is_instance_of
embedding.is-instance[OllamaEmbeddingProvider]
  Input should be an instance of OllamaEmbeddingProvider [type=is_instance_of, input_value=<core.providers.embedding...bject at 0x7f6f8cff0f50>, input_type=OpenAILikeEmbeddingProvider]
    For further information visit https://errors.pydantic.dev/2.11/v/is_instance_of while creating R2RProviders.
2025-09-05 10:12:07 - ERROR - Failed to start R2R server: 3 validation errors for R2RProviders
embedding.is-instance[LiteLLMEmbeddingProvider]
  Input should be an instance of LiteLLMEmbeddingProvider [type=is_instance_of, input_value=<core.providers.embedding...bject at 0x7f6f8cff0f50>, input_type=OpenAILikeEmbeddingProvider]
    For further information visit https://errors.pydantic.dev/2.11/v/is_instance_of
embedding.is-instance[OpenAIEmbeddingProvider]
  Input should be an instance of OpenAIEmbeddingProvider [type=is_instance_of, input_value=<core.providers.embedding...bject at 0x7f6f8cff0f50>, input_type=OpenAILikeEmbeddingProvider]
    For further information visit https://errors.pydantic.dev/2.11/v/is_instance_of
embedding.is-instance[OllamaEmbeddingProvider]
  Input should be an instance of OllamaEmbeddingProvider [type=is_instance_of, input_value=<core.providers.embedding...bject at 0x7f6f8cff0f50>, input_type=OpenAILikeEmbeddingProvider]
    For further information visit https://errors.pydantic.dev/2.11/v/is_instance_of
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/mnt/nvme1/workspace/R2R/py/r2r/serve.py", line 222, in <module>
    main()
  File "/mnt/nvme1/workspace/R2R/py/r2r/serve.py", line 212, in main
    run_server(
  File "/mnt/nvme1/workspace/R2R/py/r2r/serve.py", line 174, in run_server
    raise e
  File "/mnt/nvme1/workspace/R2R/py/r2r/serve.py", line 171, in run_server
    asyncio.run(start())
  File "/root/.pyenv/versions/3.12.9/lib/python3.12/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.12.9/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.pyenv/versions/3.12.9/lib/python3.12/asyncio/base_events.py", line 691, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/mnt/nvme1/workspace/R2R/py/r2r/serve.py", line 168, in start
    app = await create_app(config_name, config_path, full)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/nvme1/workspace/R2R/py/r2r/serve.py", line 51, in create_app
    r2r_instance = await R2RBuilder(
                   ^^^^^^^^^^^^^^^^^
  File "/mnt/nvme1/workspace/R2R/py/core/main/assembly/builder.py", line 65, in build
    providers = await self._create_providers(
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/nvme1/workspace/R2R/py/core/main/assembly/builder.py", line 146, in _create_providers
    return await factory.create_providers(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/nvme1/workspace/R2R/py/core/main/assembly/factory.py", line 488, in create_providers
    return R2RProviders(
           ^^^^^^^^^^^^^
  File "/root/.pyenv/versions/r2r/lib/python3.12/site-packages/pydantic/main.py", line 253, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 3 validation errors for R2RProviders
embedding.is-instance[LiteLLMEmbeddingProvider]
  Input should be an instance of LiteLLMEmbeddingProvider [type=is_instance_of, input_value=<core.providers.embedding...bject at 0x7f6f8cff0f50>, input_type=OpenAILikeEmbeddingProvider]
    For further information visit https://errors.pydantic.dev/2.11/v/is_instance_of
embedding.is-instance[OpenAIEmbeddingProvider]
  Input should be an instance of OpenAIEmbeddingProvider [type=is_instance_of, input_value=<core.providers.embedding...bject at 0x7f6f8cff0f50>, input_type=OpenAILikeEmbeddingProvider]
    For further information visit https://errors.pydantic.dev/2.11/v/is_instance_of
embedding.is-instance[OllamaEmbeddingProvider]
  Input should be an instance of OllamaEmbeddingProvider [type=is_instance_of, input_value=<core.providers.embedding...bject at 0x7f6f8cff0f50>, input_type=OpenAILikeEmbeddingProvider]
    For further information visit https://errors.pydantic.dev/2.11/v/is_instance_of
(r2r) [root@pae-llm-host py]# 