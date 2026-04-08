FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY workplace_ai_env/server/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy application code
COPY workplace_ai_env/ /app/workplace_ai_env/
COPY inference.py /app/inference.py
COPY pyproject.toml /app/pyproject.toml

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "workplace_ai_env.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
