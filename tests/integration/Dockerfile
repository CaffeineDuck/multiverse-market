FROM python:3.12-slim-bookworm

RUN useradd -m -u 1000 app

WORKDIR /app

COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies including test dependencies
RUN pip install -e ".[test]"

# Create directory for SQLite database and ensure it's writable
RUN mkdir -p /app/data && \
    chown -R app:app /app && \
    chmod -R 755 /app

USER app

ENV PYTHONPATH=/app

CMD ["pytest", "tests/integration", "-v", "--cov=src", "--cov-report=term-missing"] 