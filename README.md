# Multiverse Market

A marketplace system for trading across multiple parallel universes.

## Quick Start

1. Clone the repository

2. Set up environment:
```bash
cp env/.env.template env/.env
# Edit env/.env with your configuration
```

3. Start the application:
```bash
make docker/build  # Build containers
make docker/up     # Start containers
make docker/migrate  # Run migrations
make docker/seed     # Seed data
```

## Available Commands

```
Usage:
  make [target]

Targets:
  docker/build         Build or rebuild services
  docker/clean-volumes Remove all volumes (WARNING: destroys data)
  docker/down          Stop and remove containers (preserves volumes)
  docker/logs          View output from containers
  docker/migrate       Run database migrations in Docker
  docker/restart       Restart all containers (preserves volumes)
  docker/seed          Seed the database in Docker
  docker/shell         Open a shell in the app container
  docker/test          Run tests in Docker
  docker/up            Create and start containers
  help                 Show this help message
  migrate              Run database migrations locally
  seed                 Seed the database locally
  test                 Run tests locally
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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

## Features

- Currency exchange between different universes
- Cross-universe item trading
- Transaction history tracking
- Redis caching for improved performance
- PostgreSQL database for persistent storage

## Database Schema

- **Universes**: Store details about each universe (name, currency type, exchange rate)
- **Users**: Store user data (username, current universe, balance)
- **Items**: Store details about items available for trade
- **Transactions**: Store transaction history

## Scalability

The system is designed to handle thousands of transactions per minute:
- Redis caching for frequently accessed data
- Database indexing for improved query performance
- Efficient currency conversion handling 