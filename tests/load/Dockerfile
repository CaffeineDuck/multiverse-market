FROM python:3.12-slim-bookworm

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy project files
COPY pyproject.toml .
COPY src src/

# Create venv and install dependencies with test extras
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install -e ".[test]"

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set Python path and activate venv
ENV PYTHONPATH=/app \
    PATH=/app/.venv/bin:$PATH

# Default command to run Locust
CMD ["locust", "--host", "${API_URL:-http://app:8000}"] 