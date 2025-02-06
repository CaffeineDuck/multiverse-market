FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./
COPY src src/

# Create venv and install dependencies
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install -e .

# Final stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy the venv from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Copy project files
COPY pyproject.toml .
COPY alembic.ini* .
COPY migrations* migrations/

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set Python path and activate venv
ENV PYTHONPATH=/app \
    PATH=/app/.venv/bin:$PATH

CMD ["uvicorn", "multiverse_market.main:app", "--host", "0.0.0.0", "--port", "8000"] 