from decimal import Decimal
import json
from datetime import datetime
import typing as ty

from ..interfaces import CacheBackend, MarketBackend
from ..repositories import UserRepository, ItemRepository, TransactionRepository, UniverseRepository
from ..models.entities import Transaction
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
    
    async def _get_cached_exchange_rate(self, from_universe_id: int, to_universe_id: int) -> Decimal:
        cache_key = f"exchange_rate:{from_universe_id}:{to_universe_id}"
        cached_rate = await self._cache.get(cache_key)
        
        if cached_rate:
            return Decimal(cached_rate)
        
        universes = await self._universes.list()
        from_universe = next((u for u in universes if u.id == from_universe_id), None)
        to_universe = next((u for u in universes if u.id == to_universe_id), None)
        
        if not from_universe or not to_universe:
            raise UniverseNotFoundException()
        
        rate = Decimal(str(to_universe.exchange_rate / from_universe.exchange_rate))
        await self._cache.setex(cache_key, 3600, str(rate))
        return rate

    async def exchange_currency(self, exchange: CurrencyExchange) -> CurrencyExchangeResponse:
        user = await self._users.get(exchange.user_id)
        if not user:
            raise UserNotFoundException()
        if user.balance < exchange.amount:
            raise InsufficientBalanceException()
        
        exchange_rate = await self._get_cached_exchange_rate(
            exchange.from_universe_id,
            exchange.to_universe_id
        )
        
        converted_amount = Decimal(str(exchange.amount)) * exchange_rate
        new_balance = float(Decimal(str(user.balance)) - Decimal(str(exchange.amount)) + converted_amount)
        await self._users.update_balance(user.id, new_balance)
        
        return CurrencyExchangeResponse(
            converted_amount=float(converted_amount),
            from_universe_id=exchange.from_universe_id,
            to_universe_id=exchange.to_universe_id,
            exchange_rate=float(exchange_rate)
        )

    async def buy_item(self, purchase: ItemPurchase) -> TransactionSchema:
        cache_key = f"item:{purchase.item_id}"
        cached_item = await self._cache.get(cache_key)
        
        if cached_item:
            item_data: ItemCache = json.loads(cached_item)
            item = await self._items.get(purchase.item_id)
            if item and item.stock != item_data["stock"]:
                await self._cache.delete(cache_key)
        
        item = await self._items.get(purchase.item_id)
        if not item:
            raise ItemNotFoundException()
        
        buyer = await self._users.get(purchase.buyer_id)
        if not buyer:
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
            transaction_time=datetime.utcnow()
        )
        
        await self._users.update_balance(buyer.id, float(Decimal(str(buyer.balance)) - total_cost))
        await self._items.update_stock(item.id, item.stock - purchase.quantity)
        transaction = await self._transactions.add(transaction)
        
        await self._cache.setex(
            cache_key,
            3600,
            json.dumps({"id": item.id, "stock": item.stock - purchase.quantity, "price": item.price})
        )
        
        return TransactionSchema.model_validate(transaction)

    async def get_user(self, user_id: int) -> UserSchema:
        user = await self._users.get(user_id)
        if not user:
            raise UserNotFoundException()
        return UserSchema.model_validate(user)

    async def list_items(self, universe_id: int | None = None) -> ty.Sequence[ItemSchema]:
        items = await self._items.list(universe_id=universe_id)
        return [ItemSchema.model_validate(item) for item in items]

    async def list_universes(self) -> ty.Sequence[UniverseSchema]:
        universes = await self._universes.list()
        return [UniverseSchema.model_validate(u) for u in universes]

    async def get_user_trades(self, user_id: int) -> ty.Sequence[TransactionSchema]:
        transactions = await self._transactions.get_user_trades(user_id)
        return [TransactionSchema.model_validate(tx) for tx in transactions] 