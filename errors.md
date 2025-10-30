---------------------------------------------------------------------------
R2RException                              Traceback (most recent call last)
Cell In[16], line 12
     10                 target_file = os.path.join(root, file)
     11                 print(target_file)
---> 12                 client.documents.create(target_file)
     13                 print(target_file+'is loaded...')
     14 # existed_docs = client.documents.list()
     15 # existed_filenames = []
     16 # for doc in existed_docs:
   (...)     22 #     client.documents.create(os.path.join(base, file))
     23 #     print("finish doc")

File /mnt/nvme1/workspace/R2R/py/sdk/sync_methods/documents.py:120, in DocumentsSDK.create(self, file_path, raw_text, chunks, s3_url, id, ingestion_mode, collection_ids, metadata, ingestion_config, run_with_orchestration)
    113 files = [
    114     (
    115         "file",
    116         (filename, file_instance, "application/octet-stream"),
    117     )
    118 ]
    119 try:
--> 120     response_dict = self.client._make_request(
    121         "POST",
    122         "documents",
    123         data=data,
    124         files=files,
    125         version="v3",
    126     )
    127 finally:
    128     # Ensure we close the file after the request is complete
    129     file_instance.close()

File /mnt/nvme1/workspace/R2R/py/sdk/sync_client.py:52, in R2RClient._make_request(self, method, endpoint, version, **kwargs)
     50 try:
     51     response = self.client.request(method, url, **request_args)
---> 52     self._handle_response(response)
     54     if "application/json" in response.headers.get("Content-Type", ""):
     55         return response.json() if response.content else None

File /mnt/nvme1/workspace/R2R/py/sdk/sync_client.py:145, in R2RClient._handle_response(self, response)
    142 except Exception as e:
    143     message = str(e)
--> 145 raise R2RException(
    146     status_code=response.status_code, message=message
    147 )

R2RException: An error '500: Error during ingestion: 'AsyncStream' object has no attribute 'dict'' occurred during create_document