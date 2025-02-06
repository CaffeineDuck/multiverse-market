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

## Setup

1. Clone the repository
2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

3. Create a PostgreSQL database:
```bash
createdb multiverse_market
```

4. Create a `.env` file with your configuration:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/multiverse_market
REDIS_URL=redis://localhost:6379/0
```

5. Run the application:
```bash
uvicorn multiverse_market.main:app --reload
```

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation at: http://localhost:8000/docs
- ReDoc documentation at: http://localhost:8000/redoc

## API Endpoints

- `POST /api/exchange_currency`: Convert currency between universes
- `POST /api/buy_item`: Purchase items from other universes
- `GET /api/my_trades/{user_id}`: View user's trade history

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