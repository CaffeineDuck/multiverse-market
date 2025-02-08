import typing as ty

from .models import (
    CurrencyExchange,
    CurrencyExchangeResponse,
    ItemPurchase,
    ItemSchema,
    TransactionSchema,
    UniverseSchema,
    UserSchema,
)


class CacheBackend(ty.Protocol):
    """Protocol for cache operations."""

    async def get(self, key: str) -> str | None:
        """Get value from cache."""
        ...

    async def setex(self, key: str, expires: int, value: str) -> None:
        """Set value in cache with expiration."""
        ...

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        ...


class DatabaseBackend(ty.Protocol):
    """Protocol for database operations."""

    async def get_user(self, user_id: int) -> UserSchema | None:
        """Get user by ID."""
        ...

    async def get_item(self, item_id: int) -> ItemSchema | None:
        """Get item by ID."""
        ...

    async def list_universes(self) -> ty.Sequence[UniverseSchema]:
        """List all universes."""
        ...

    async def list_items(self, universe_id: int | None = None) -> ty.Sequence[ItemSchema]:
        """List items, optionally filtered by universe."""
        ...

    async def get_user_trades(self, user_id: int) -> ty.Sequence[TransactionSchema]:
        """Get user's trade history."""
        ...

    async def update_user_balance(self, user_id: int, new_balance: float) -> None:
        """Update user's balance."""
        ...

    async def update_item_stock(self, item_id: int, new_stock: int) -> None:
        """Update item's stock."""
        ...

    async def save_transaction(self, transaction: TransactionSchema) -> None:
        """Save a new transaction."""
        ...


class MarketBackend(ty.Protocol):
    """Protocol for market operations."""

    async def exchange_currency(self, exchange: CurrencyExchange) -> CurrencyExchangeResponse:
        """Exchange currency between universes."""
        ...

    async def buy_item(self, purchase: ItemPurchase) -> TransactionSchema:
        """Purchase an item."""
        ...

    async def get_user(self, user_id: int) -> UserSchema:
        """Get user details."""
        ...

    async def list_items(self, universe_id: int | None = None) -> ty.Sequence[ItemSchema]:
        """List available items."""
        ...

    async def list_universes(self) -> ty.Sequence[UniverseSchema]:
        """List all universes."""
        ...

    async def get_user_trades(self, user_id: int) -> ty.Sequence[TransactionSchema]:
        """Get user's trade history."""
        ...
