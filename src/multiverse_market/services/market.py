from decimal import Decimal
import json
from datetime import datetime, UTC
import typing as ty
from contextlib import asynccontextmanager

from ..interfaces import CacheBackend, MarketBackend
from ..repositories import UserRepository, ItemRepository, TransactionRepository, UniverseRepository
from ..models.entities import User, Item, Universe, Transaction
from ..models.schemas import UserSchema, ItemSchema, TransactionSchema, UniverseSchema
from ..models.requests import CurrencyExchange, ItemPurchase
from ..models import CurrencyExchangeResponse
from ..exceptions import (
    UserNotFoundException, ItemNotFoundException, UniverseNotFoundException,
    InsufficientBalanceException, InsufficientStockException
)

class ItemCache(ty.TypedDict):
    id: int
    stock: int
    price: float

class MarketService(MarketBackend):
    def __init__(
        self,
        user_repo: UserRepository,
        item_repo: ItemRepository,
        transaction_repo: TransactionRepository,
        universe_repo: UniverseRepository,
        cache: CacheBackend
    ):
        self._users = user_repo
        self._items = item_repo
        self._transactions = transaction_repo
        self._universes = universe_repo
        self._cache = cache
    
    @asynccontextmanager
    async def _transaction(self):
        """Context manager for handling database transactions."""
        try:
            yield
            await self._users._session.commit()
        except Exception:
            await self._users._session.rollback()
            raise

    async def _invalidate_exchange_rate_cache(self, universe_id: int) -> None:
        """Invalidate all exchange rate caches involving a universe."""
        universes = await self._universes.list()
        for universe in universes:
            if universe.id != universe_id:
                key1 = f"exchange_rate:{universe_id}:{universe.id}"
                key2 = f"exchange_rate:{universe.id}:{universe_id}"
                await self._cache.delete(key1)
                await self._cache.delete(key2)

    async def _invalidate_user_cache(self, user_id: int) -> None:
        """Invalidate user-related caches."""
        await self._cache.delete(f"user:{user_id}")

    async def _invalidate_item_cache(self, item_id: int) -> None:
        """Invalidate item-related caches."""
        await self._cache.delete(f"item:{item_id}")

    async def _get_cached_exchange_rate(self, from_universe_id: int, to_universe_id: int) -> Decimal:
        if from_universe_id == to_universe_id:
            raise ValueError("Cannot exchange currency within the same universe")
            
        cache_key = f"exchange_rate:{from_universe_id}:{to_universe_id}"
        cached_rate = await self._cache.get(cache_key)
        
        if cached_rate:
            return Decimal(cached_rate)
        
        from_universe = await self._universes.get(from_universe_id)
        to_universe = await self._universes.get(to_universe_id)
        
        if not from_universe or not isinstance(from_universe, Universe) or not to_universe or not isinstance(to_universe, Universe):
            raise UniverseNotFoundException()
        
        rate = Decimal(str(to_universe.exchange_rate / from_universe.exchange_rate))
        await self._cache.setex(cache_key, 3600, str(rate))
        return rate

    async def exchange_currency(self, exchange: CurrencyExchange) -> CurrencyExchangeResponse:
        async with self._transaction():
            user = await self._users.get(exchange.user_id)
            if not user or not isinstance(user, User):
                raise UserNotFoundException()
            if user.balance < exchange.amount:
                raise InsufficientBalanceException()
            
            exchange_rate = await self._get_cached_exchange_rate(
                exchange.from_universe_id,
                exchange.to_universe_id
            )
            
            converted_amount = Decimal(str(exchange.amount)) * exchange_rate
            new_balance = float(Decimal(str(user.balance)) - Decimal(str(exchange.amount)))
            await self._users.update_balance(user.id, new_balance)
            
            # Invalidate user cache after balance update
            await self._invalidate_user_cache(user.id)
            
            return CurrencyExchangeResponse(
                converted_amount=float(converted_amount),
                from_universe_id=exchange.from_universe_id,
                to_universe_id=exchange.to_universe_id,
                exchange_rate=float(exchange_rate)
            )

    async def buy_item(self, purchase: ItemPurchase) -> TransactionSchema:
        async with self._transaction():
            cache_key = f"item:{purchase.item_id}"
            cached_item = await self._cache.get(cache_key)
            
            if cached_item:
                item_data: ItemCache = json.loads(cached_item)
                item = await self._items.get(purchase.item_id)
                if item and (item.stock != item_data["stock"] or item.price != item_data["price"]):
                    # Invalidate cache if either stock or price has changed
                    await self._cache.delete(cache_key)
            
            item = await self._items.get(purchase.item_id)
            if not item or not isinstance(item, Item):
                raise ItemNotFoundException()
            
            buyer = await self._users.get(purchase.buyer_id)
            if not buyer or not isinstance(buyer, User):
                raise UserNotFoundException()
            
            if item.stock < purchase.quantity:
                raise InsufficientStockException()
            
            total_cost = Decimal(str(item.price)) * Decimal(str(purchase.quantity))
            if buyer.universe_id != item.universe_id:
                exchange_rate = await self._get_cached_exchange_rate(buyer.universe_id, item.universe_id)
                total_cost *= exchange_rate
            
            if buyer.balance < float(total_cost):
                raise InsufficientBalanceException()
            
            transaction = Transaction(
                buyer_id=buyer.id,
                seller_id=item.universe_id,
                item_id=item.id,
                amount=float(total_cost),
                quantity=purchase.quantity,
                from_universe_id=buyer.universe_id,
                to_universe_id=item.universe_id,
                transaction_time=datetime.now(UTC)
            )
            
            await self._users.update_balance(buyer.id, float(Decimal(str(buyer.balance)) - total_cost))
            await self._items.update_stock(item.id, item.stock - purchase.quantity)
            transaction = await self._transactions.add(transaction)
            
            # Invalidate affected caches
            await self._invalidate_user_cache(buyer.id)
            await self._invalidate_item_cache(item.id)
            
            return TransactionSchema.model_validate(transaction)

    async def get_user(self, user_id: int) -> UserSchema:
        user = await self._users.get(user_id)
        if not user or not isinstance(user, User):
            raise UserNotFoundException()
        return UserSchema.model_validate(user)

    async def list_items(self, universe_id: int | None = None) -> ty.Sequence[ItemSchema]:
        items = await self._items.list(universe_id=universe_id)
        return [ItemSchema.model_validate(item) for item in items if isinstance(item, Item)]

    async def list_universes(self) -> ty.Sequence[UniverseSchema]:
        universes = await self._universes.list()
        return [UniverseSchema.model_validate(u) for u in universes if isinstance(u, Universe)]

    async def get_user_trades(self, user_id: int) -> ty.Sequence[TransactionSchema]:
        transactions = await self._transactions.get_user_trades(user_id)
        return [TransactionSchema.model_validate(tx) for tx in transactions] 