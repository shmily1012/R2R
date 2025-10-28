
2025-10-28 10:29:54 - ERROR - [Errno 98] error while attempting to bind on address ('0.0.0.0', 8002): [errno 98] address already in use


The compose file still maps the app to host port 8002 (docker/compose.dev.yaml:57), so something is already listening there when you rerun py\r2r\serve.py. That “address already in use” error is Windows saying the port is taken—most often it’s either the r2r_app container from docker compose that’s still up, or a stray Python process from a previous local run.

Check who owns the port: netstat -ano | findstr :8002 or Get-NetTCPConnection -LocalPort 8002 and then kill that PID (or docker ps → docker stop <id> if it’s the container).
If you want to keep the compose stack running, launch the local server on another port instead: python py\r2r\serve.py --port 8003.
Once the port is free, rerun your command and it should bind normally.
Next step I’d suggest is docker compose -f docker/compose.dev.yaml down (or stop the specific PID you find) before restarting the service.