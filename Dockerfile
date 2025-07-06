########################################
# Stage 1: Builder (install dependencies and prepare application)
########################################
FROM python:3.10-slim AS builder

# Prevent creation of .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/opt/venv \
    PATH="$VENV_PATH/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install uv dependency manager
RUN python -m venv $VENV_PATH

# Copy dependency descriptors
WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install uv and generate requirements.txt from lock file
RUN pip install --no-cache-dir uv \
    && uv export --extra dev --format requirements-txt > /tmp/requirements.txt

# Copy application source code
COPY . /app

########################################
# Stage 2: Final (production image)
########################################
FROM python:3.10-slim AS final

# Prevent creation of .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/opt/venv \
    PATH="$VENV_PATH/bin:$PATH"

# Create non-root user and group
RUN addgroup --system appuser \
    && adduser --system --ingroup appuser appuser

# Copy virtual environment and application, setting correct ownership
COPY --from=builder --chown=appuser:appuser $VENV_PATH $VENV_PATH
COPY --from=builder --chown=appuser:appuser /app /app
COPY --from=builder /tmp/requirements.txt /app/requirements.txt

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && rm /app/requirements.txt

# Set up cache directory for any future needs
RUN mkdir -p /home/appuser/.cache \
    && chown -R appuser:appuser /home/appuser/.cache

# Set working directory and user
WORKDIR /app
USER appuser

# Expose port for Gunicorn
EXPOSE 8000

# Start the application using Gunicorn with WSGI
CMD ["gunicorn", "blog_api.wsgi:application", \
     "-b", "0.0.0.0:8000", \
     "--access-logfile", "-"]