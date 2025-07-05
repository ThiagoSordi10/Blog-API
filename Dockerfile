# Stage 1: Build (install dependencies and prepare assets)
FROM python:3.10-slim AS builder

# Environment variables: no .pyc files, unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv dependency manager
RUN pip install --no-cache-dir uv

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv sync with dev extras
RUN uv sync --extra dev

# Copy the rest of the source code
COPY . .

# Stage 2: Final (minimal image for production)
FROM python:3.10-slim

# Create non-root user
RUN useradd --create-home appuser

WORKDIR /app

# Copy only the built app and venv from builder
COPY --from=builder /app /app

# Set permissions
RUN chown -R appuser:appuser /app
USER appuser

# Expose default Gunicorn port
EXPOSE 8000

# Startup command: Gunicorn with ASGI
CMD ["uv", "run", "gunicorn", "blog_api.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--access-logfile", "-"] 