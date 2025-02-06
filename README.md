# Multiverse Market

A marketplace system for trading across multiple parallel universes. Users can buy and sell goods across different universes, each with its own economy, currency, and trading rules.

## Features

- Currency exchange between different universes
- Cross-universe item trading
- Transaction history tracking
- Redis caching for improved performance
- PostgreSQL database for persistent storage

## Setup with Docker

1. Clone the repository

2. Set up environment variables:
```bash
cp env/.env.template env/.env
# Edit env/.env with your configuration
```

3. Build and start the containers:
```bash
make build  # Build the containers
make up     # Start the containers
```

4. Run migrations and seed data:
```bash
make migrate  # Run database migrations
make seed     # Seed test data
```

You can view all available commands with:
```bash
make help
```

Common commands:
- Docker management:
  - `make build` - Build containers
  - `make up` - Start containers
  - `make down` - Stop containers
  - `make ps` - List containers
  - `make logs` - View container logs
  - `make restart` - Restart all containers (preserves data)

- Development commands:
  - Local:
    - `make test` - Run tests locally
    - `make migrate` - Run migrations locally
    - `make seed` - Seed database locally
    - `make shell` - Open a local shell
  - Docker:
    - `make docker/test` - Run tests in Docker
    - `make docker/migrate` - Run migrations in Docker
    - `make docker/seed` - Seed database in Docker
    - `make docker/shell` - Open shell in Docker container

- Cleanup:
  - `make clean` - Stop containers and clean cache files (preserves data)
  - `make clean-volumes` - Remove all volumes (WARNING: destroys data)
  - `make clean-all` - Full cleanup including volumes (WARNING: destroys all data)

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation at: http://localhost:8000/docs
- ReDoc documentation at: http://localhost:8000/redoc

For detailed API endpoints and schema, please refer to the documentation above.

## Development

### Running Tests
```bash
make test
```

### Code Quality
The project uses ruff for linting and formatting. Configuration can be found in pyproject.toml.

### Database Migrations

To create a new migration:
```bash
docker compose exec app alembic revision --autogenerate -m "description of changes"
```

To apply migrations:
```bash
make migrate
```

To rollback migrations:
```bash
docker compose exec app alembic downgrade -1  # Rollback one migration
docker compose exec app alembic downgrade base  # Rollback all migrations
```

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