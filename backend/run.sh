#!/usr/bin/env sh
# Production: set PORT in env (e.g. Railway, Render). Local: defaults to 8000.
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
