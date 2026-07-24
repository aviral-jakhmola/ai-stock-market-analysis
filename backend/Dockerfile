FROM python:3.13-slim AS base

# Prevents .pyc files and forces stdout/stderr to be unbuffered (so logs
# show up immediately in `docker logs`, not just on container exit)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# Install build-time system deps needed by some Python packages (e.g. cryptography),
# then remove apt caches to keep the image lean
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .

# torch is installed separately from the CPU-only wheel index — the default
# PyPI torch wheel bundles CUDA support, which isn't needed for a CPU-only
# deployment and adds several GB to the image for nothing.
RUN grep -v "^torch==" requirements.txt > requirements-notorch.txt \
    && pip install -r requirements-notorch.txt \
    && pip install $(grep "^torch==" requirements.txt) --index-url https://download.pytorch.org/whl/cpu

RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='ProsusAI/finbert')"

# Only copy what the app actually needs at runtime — not tests, not the venv,
# not .env (secrets should never be baked into an image layer)
COPY app/ ./app/

# Run as non-root — reduces blast radius if the container is ever compromised
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]