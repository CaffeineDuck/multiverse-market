# Multiverse Market

A marketplace system for trading across multiple parallel universes.

> **Note**: This project is intentionally over-engineered as it was created as a technical assignment to demonstrate advanced patterns and practices. While it may be excessive for a simple marketplace, it serves as a reference implementation showcasing:
> - Clean architecture with proper separation of concerns
> - Integration, unit, and load testing setups
> - Async database and caching patterns
> - Type safety and modern Python practices
> - Docker-based development workflow
>
> For simpler applications, consider a more straightforward approach. However, this codebase can be a valuable reference for scaling FastAPI applications with production-grade practices.

## Quick Start

### Setup
```bash
cp env/.env.template env/.env  # Configure environment
make docker/up                 # Start services
make docker/migrate           # Run database migrations
make docker/seed             # Seed initial data
```

### Git Hooks Setup
```bash
./install-hooks.sh  # Install git hooks (runs unit tests before commits)
```

### Access the API
- http://localhost:8000/api/v1/
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)


## Testing Commands

```bash
# Integration Tests
docker/test/integration       # Run integration tests
docker/test/integration/watch # Run integration tests in watch mode
docker/test/integration/logs  # View integration test logs

# Load Tests
docker/loadtest              # Start load testing environment
docker/loadtest/logs         # View load test logs
docker/loadtest/stop         # Stop load testing environment
```

## Features

- Cross-universe currency exchange and item trading
- Transaction history tracking
- Redis caching for performance
- PostgreSQL for persistent storage

## Scalability & Performance

The system is designed for high throughput and reliability:

- **Load Testing Results**:
  - Handles 1200+ requests/minute with <1% error rate
  - Supports 100+ concurrent users during peak loads
  - Average response time under 50ms for read operations
  - 99th percentile latency under 100ms for write operations

- **Architecture Optimizations**:
  - Redis caching for frequently accessed data (user balances, item stocks)
  - Async database operations with connection pooling
  - Efficient currency conversion handling with pre-calculated rates
  - Optimized database queries with proper indexing

- **Monitoring & Reliability**:
  - Health check endpoints for service monitoring
  - Graceful degradation under heavy load
  - Automatic retry mechanisms for transient failures
  - Comprehensive error tracking and logging

## Database Schema

- **Universes**: Universe details (name, currency, exchange rate)
- **Users**: User data (username, universe, balance)
- **Items**: Available items for trade
- **Transactions**: Transaction history

## Database Migrations

Create migration:
```bash
docker compose exec app alembic revision --autogenerate -m "description"
```

Apply/rollback:
```bash
make docker/migrate  # Apply migrations
docker compose exec app alembic downgrade -1  # Rollback one
```