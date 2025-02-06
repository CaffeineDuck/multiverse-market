from decimal import Decimal
import json
import typing as ty
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from fastapi import HTTPException

from .models import (
    UserDB, ItemDB, TransactionDB, UniverseDB,
    UserSchema, ItemSchema, UniverseSchema, TransactionSchema,
    CurrencyExchange, ItemPurchase
)
from .interfaces import CacheBackend, DatabaseBackend, MarketBackend

class ItemCache(ty.TypedDict):
    id: int
    stock: int
    price: float

class RedisCache(CacheBackend):
    def __init__(self, redis: Redis) -> None:
        self._redis = redis
    
    async def get(self, key: str) -> str | None:
        return await self._redis.get(key)
    
    async def setex(self, key: str, expires: int, value: str) -> None:
        await self._redis.setex(key, expires, value)
    
    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

class SQLAlchemyDatabase(DatabaseBackend):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
    
    async def get_user(self, user_id: int) -> UserSchema | None:
        result = await self._db.execute(select(UserDB).where(UserDB.id == user_id))
        user = result.scalar_one_or_none()
        return UserSchema.from_orm(user) if user else None
    
    async def get_item(self, item_id: int) -> ItemSchema | None:
        result = await self._db.execute(select(ItemDB).where(ItemDB.id == item_id))
        item = result.scalar_one_or_none()
        return ItemSchema.from_orm(item) if item else None
    
    async def list_universes(self) -> list[UniverseSchema]:
        result = await self._db.execute(select(UniverseDB))
        universes = result.scalars().all()
        return [UniverseSchema.from_orm(u) for u in universes]
    
    async def list_items(self, universe_id: int | None = None) -> list[ItemSchema]:
        query = select(ItemDB)
        if universe_id is not None:
            query = query.where(ItemDB.universe_id == universe_id)
        result = await self._db.execute(query)
        items = result.scalars().all()
        return [ItemSchema.from_orm(item) for item in items]
    
    async def get_user_trades(self, user_id: int) -> list[TransactionSchema]:
        result = await self._db.execute(
            select(TransactionDB)
            .where((TransactionDB.buyer_id == user_id) | (TransactionDB.seller_id == user_id))
            .order_by(TransactionDB.transaction_time.desc())
        )
        transactions = result.scalars().all()
        return [TransactionSchema.from_orm(tx) for tx in transactions]
    
    async def update_user_balance(self, user_id: int, new_balance: float) -> None:
        result = await self._db.execute(select(UserDB).where(UserDB.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.balance = new_balance
            await self._db.commit()
    
    async def update_item_stock(self, item_id: int, new_stock: int) -> None:
        result = await self._db.execute(select(ItemDB).where(ItemDB.id == item_id))
        item = result.scalar_one_or_none()
        if item:
            item.stock = new_stock
            await self._db.commit()
    
    async def save_transaction(self, transaction: TransactionSchema) -> None:
        db_transaction = TransactionDB(**transaction.dict())
        self._db.add(db_transaction)
        await self._db.commit()

class MarketService(MarketBackend):
    def __init__(self, db: DatabaseBackend, cache: CacheBackend) -> None:
        self._db = db
        self._cache = cache
    
    async def _get_cached_exchange_rate(self, from_universe_id: int, to_universe_id: int) -> Decimal:
        cache_key = f"exchange_rate:{from_universe_id}:{to_universe_id}"
        cached_rate = await self._cache.get(cache_key)
        
        if cached_rate:
            return Decimal(cached_rate)
        
        universes = await self._db.list_universes()
        from_universe = next((u for u in universes if u.id == from_universe_id), None)
        to_universe = next((u for u in universes if u.id == to_universe_id), None)
        
        if not from_universe or not to_universe:
            raise HTTPException(status_code=404, detail="Universe not found")
        
        rate = Decimal(str(to_universe.exchange_rate / from_universe.exchange_rate))
        await self._cache.setex(cache_key, 3600, str(rate))
        return rate

    async def exchange_currency(self, exchange: CurrencyExchange) -> Decimal:
        user = await self._db.get_user(exchange.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.balance < exchange.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        exchange_rate = await self._get_cached_exchange_rate(
            exchange.from_universe_id,
            exchange.to_universe_id
        )
        
        converted_amount = Decimal(str(exchange.amount)) * exchange_rate
        new_balance = float(Decimal(str(user.balance)) - Decimal(str(exchange.amount)) + converted_amount)
        await self._db.update_user_balance(user.id, new_balance)
        
        return converted_amount

    async def buy_item(self, purchase: ItemPurchase) -> TransactionSchema:
        cache_key = f"item:{purchase.item_id}"
        cached_item = await self._cache.get(cache_key)
        
        if cached_item:
            item_data: ItemCache = json.loads(cached_item)
            item = await self._db.get_item(purchase.item_id)
            if item and item.stock != item_data["stock"]:
                await self._cache.delete(cache_key)
        
        item = await self._db.get_item(purchase.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        buyer = await self._db.get_user(purchase.buyer_id)
        if not buyer:
            raise HTTPException(status_code=404, detail="Buyer not found")
        
        if item.stock < purchase.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        
        total_cost = Decimal(str(item.price)) * Decimal(str(purchase.quantity))
        if buyer.universe_id != item.universe_id:
            exchange_rate = await self._get_cached_exchange_rate(buyer.universe_id, item.universe_id)
            total_cost *= exchange_rate
        
        if buyer.balance < float(total_cost):
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        transaction = TransactionSchema(
            id=None,
            buyer_id=buyer.id,
            seller_id=item.universe_id,
            item_id=item.id,
            amount=float(total_cost),
            quantity=purchase.quantity,
            from_universe_id=buyer.universe_id,
            to_universe_id=item.universe_id,
            transaction_time=datetime.utcnow()
        )
        
        await self._db.update_user_balance(buyer.id, float(Decimal(str(buyer.balance)) - total_cost))
        await self._db.update_item_stock(item.id, item.stock - purchase.quantity)
        await self._db.save_transaction(transaction)
        
        await self._cache.setex(
            cache_key,
            3600,
            json.dumps({"id": item.id, "stock": item.stock - purchase.quantity, "price": item.price})
        )
        
        return transaction

    async def get_user(self, user_id: int) -> UserSchema:
        user = await self._db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def list_items(self, universe_id: int | None = None) -> list[ItemSchema]:
        return await self._db.list_items(universe_id)

    async def list_universes(self) -> list[UniverseSchema]:
        return await self._db.list_universes()

    async def get_user_trades(self, user_id: int) -> list[TransactionSchema]:
        return await self._db.get_user_trades(user_id) 