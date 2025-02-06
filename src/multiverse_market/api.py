from fastapi import APIRouter
from typing import List
from .models import (
    UserSchema, ItemSchema, TransactionSchema, UniverseSchema,
    CurrencyExchange, ItemPurchase
)
from .dependencies import MarketDependency

router = APIRouter()

@router.get("/universes", response_model=List[UniverseSchema])
async def list_universes(market: MarketDependency):
    """List all available universes."""
    return await market.list_universes()

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, market: MarketDependency):
    """Get user details."""
    return await market.get_user(user_id)

@router.get("/items", response_model=List[ItemSchema])
async def list_items(market: MarketDependency, universe_id: int | None = None):
    """List available items, optionally filtered by universe."""
    return await market.list_items(universe_id)

@router.post("/exchange", response_model=float)
async def exchange_currency(exchange: CurrencyExchange, market: MarketDependency):
    """Exchange currency between universes."""
    return float(await market.exchange_currency(exchange))

@router.post("/buy", response_model=TransactionSchema)
async def buy_item(purchase: ItemPurchase, market: MarketDependency):
    """Purchase an item."""
    return await market.buy_item(purchase)

@router.get("/trades/{user_id}", response_model=List[TransactionSchema])
async def get_user_trades(user_id: int, market: MarketDependency):
    """Get all trades for a user."""
    return await market.get_user_trades(user_id) 