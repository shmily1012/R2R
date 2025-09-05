2025-09-05 10:54:28 - INFO - Creating table, if it does not exist: "r2r_local"."documents"
2025-09-05 10:54:28 - ERROR - Error Dimension mismatch: Table 'r2r_local.chunks' was created with dimension 1536, but 2560 was provided. You must use the same dimension for existing tables. while creating R2RProviders.
2025-09-05 10:54:28 - ERROR - Failed to start R2R server: Dimension mismatch: Table 'r2r_local.chunks' was created with dimension 1536, but 2560 was provided. You must use the same dimension for existing tables.
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
  File "/mnt/nvme1/workspace/R2R/py/core/main/assembly/factory.py", line 434, in create_providers
    or await self.create_database_provider(
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/nvme1/workspace/R2R/py/core/main/assembly/factory.py", line 229, in create_database_provider
    await database_provider.initialize()
  File "/mnt/nvme1/workspace/R2R/py/core/providers/database/postgres.py", line 229, in initialize
    await self.chunks_handler.create_tables()
  File "/mnt/nvme1/workspace/R2R/py/core/providers/database/chunks.py", line 128, in create_tables
    raise ValueError(
ValueError: Dimension mismatch: Table 'r2r_local.chunks' was created with dimension 1536, but 2560 was provided. You must use the same dimension for existing tables.