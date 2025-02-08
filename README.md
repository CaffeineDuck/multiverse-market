# Multiverse Market

A marketplace system for trading across multiple parallel universes.

## Quick Start

### Setup
```bash
cp env/.env.template env/.env  # Configure environment
make docker/up                 # Start services
make docker/migrate           # Run database migrations
make docker/seed             # Seed initial data
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

## Scalability

The system is designed to handle thousands of transactions per minute:
- Redis caching for frequently accessed data
- Database indexing for improved query performance
- Efficient currency conversion handling 