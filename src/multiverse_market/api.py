import logging

from fastapi import APIRouter

from multiverse_market.models.responses import CurrencyExchangeResponse

from .dependencies import MarketDependency
from .models.requests import CurrencyExchange, ItemPurchase
from .models.schemas import (
    ItemSchema,
    TransactionSchema,
    UniverseSchema,
    UserSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/universes", response_model=list[UniverseSchema])
async def list_universes(market: MarketDependency):
    """List all available universes."""
    logger.debug("Handling request to list universes")
    return await market.list_universes()


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, market: MarketDependency):
    """Get user details."""
    logger.debug(f"Handling request to get user {user_id}")
    return await market.get_user(user_id)


@router.get("/items", response_model=list[ItemSchema])
async def list_items(market: MarketDependency, universe_id: int | None = None):
    """List available items, optionally filtered by universe."""
    logger.debug(f"Handling request to list items for universe {universe_id}")
    return await market.list_items(universe_id)


@router.post("/exchange", response_model=CurrencyExchangeResponse)
async def exchange_currency(exchange: CurrencyExchange, market: MarketDependency):
    """Exchange currency between universes."""
    logger.info(f"Processing currency exchange request for user {exchange.user_id}")
    return await market.exchange_currency(exchange)


@router.post("/buy", response_model=TransactionSchema)
async def buy_item(purchase: ItemPurchase, market: MarketDependency):
    """Purchase an item."""
    logger.info(f"Processing purchase request for user {purchase.buyer_id}")
    return await market.buy_item(purchase)


@router.get("/trades/{user_id}", response_model=list[TransactionSchema])
async def get_user_trades(user_id: int, market: MarketDependency):
    """Get all trades for a user."""
    return await market.get_user_trades(user_id)
