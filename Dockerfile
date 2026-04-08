FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY workplace_ai_env/server/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Install huggingface-hub for inference support
RUN pip install --no-cache-dir huggingface-hub httpx pydantic

# Copy application code
COPY workplace_ai_env/ /app/workplace_ai_env/
COPY server/ /app/server/
COPY app.py /app/app.py
COPY inference.py /app/inference.py
COPY pyproject.toml /app/pyproject.toml
COPY models.py /app/models.py
COPY __init__.py /app/__init__.py
COPY entrypoint.sh /app/entrypoint.sh

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
