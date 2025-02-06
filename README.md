# Multiverse Market

A marketplace system for trading across multiple parallel universes. Users can buy and sell goods across different universes, each with its own economy, currency, and trading rules.

## Features

- Currency exchange between different universes
- Cross-universe item trading
- Transaction history tracking
- Redis caching for improved performance
- PostgreSQL database for persistent storage

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Docker and Docker Compose (for containerized setup)

## Setup

### Local Development

1. Clone the repository
2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

3. Set up environment variables:
```bash
cp env/.env.template env/.env
# Edit env/.env with your configuration
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Seed the database with test data:
```bash
python -m multiverse_market.cli seed
```

6. Run the application:
```bash
uvicorn multiverse_market.main:app --reload
```

### Docker Setup

1. Clone the repository

2. Set up environment variables:
```bash
cp env/.env.template env/.env
# Edit env/.env with your configuration
```

3. Build and start the containers:
```bash
docker compose up -d
```

4. Run migrations and seed data:
```bash
docker compose exec app alembic upgrade head
docker compose exec app python -m multiverse_market.cli seed
```

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation at: http://localhost:8000/docs
- ReDoc documentation at: http://localhost:8000/redoc

## API Endpoints

- `POST /api/v1/exchange`: Convert currency between universes
- `POST /api/v1/buy`: Purchase items from other universes
- `GET /api/v1/trades/{user_id}`: View user's trade history
- `GET /api/v1/users/{user_id}`: Get user details
- `GET /api/v1/items`: List available items (optional universe_id filter)
- `GET /api/v1/universes`: List all universes

## Development

### Running Tests
```bash
pip install ".[test]"
pytest
```

### Code Quality
The project uses ruff for linting and formatting. Configuration can be found in pyproject.toml.

### Database Migrations

To create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

To apply migrations:
```bash
alembic upgrade head
```

To rollback migrations:
```bash
alembic downgrade -1  # Rollback one migration
alembic downgrade base  # Rollback all migrations
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