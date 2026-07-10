FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy packaging metadata first for better layer caching
COPY pyproject.toml ./
COPY README.md ./

# Copy source package(s)
COPY app ./app

# Install project using pyproject configuration
RUN pip install --upgrade pip && pip install .

# Runtime configuration
ENV HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host ${HOST} --port ${PORT}"]
