#!/bin/bash
# Entrypoint script for WorkplaceAIEnv++ Docker container
set -e

echo "[Startup] WorkplaceAIEnv++ Server"
echo "[Startup] Validating environment..."
echo "[Startup] API_BASE_URL=${API_BASE_URL:-https://router.huggingface.co/hf-inference/v1}"
echo "[Startup] MODEL_NAME=${MODEL_NAME:-meta-llama/Llama-3.1-8B-Instruct}"
echo "[Startup] ENV_SERVER_URL=${ENV_SERVER_URL:-http://localhost:8000}"
if [ -n "$HF_TOKEN" ]; then
    echo "[Startup] HF_TOKEN: set (first 10 chars: ${HF_TOKEN:0:10}...)"
else
    echo "[Startup] HF_TOKEN: not set (optional for validation mode)"
fi
echo "[Startup] Starting FastAPI server..."

exec uvicorn workplace_ai_env.server.app:app --host 0.0.0.0 --port 8000
