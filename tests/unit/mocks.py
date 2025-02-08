from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from multiverse_market.exceptions import (
    ItemNotFoundException,
    UniverseNotFoundException,
    UserNotFoundException,
)
from multiverse_market.interfaces import CacheBackend
from multiverse_market.models.entities import Item, Transaction, Universe, User
from multiverse_market.repositories import (
    ItemRepository,
    TransactionRepository,
    UniverseRepository,
    UserRepository,
)


class MockSession:
    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


class InMemoryCacheService(CacheBackend):
    def __init__(self):
        self._cache: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._cache.get(key)

    async def setex(self, key: str, expires: int, value: str) -> None:
        self._cache[key] = value

    async def delete(self, key: str) -> None:
        self._cache.pop(key, None)


class MockUserRepository(UserRepository):
    def __init__(self):
        self._users: dict[int, User] = {}
        self._session = MockSession()

    async def get(self, id: int) -> User | None:
        return self._users.get(id)

    async def list(self, **filters) -> Sequence[User]:
        return list(self._users.values())

    async def update_balance(self, user_id: int, new_balance: float) -> None:
        user = await self.get(user_id)
        if not user:
            raise UserNotFoundException()
        self._users[user_id] = User(
            id=user.id, username=user.username, universe_id=user.universe_id, balance=new_balance
        )


class MockItemRepository(ItemRepository):
    def __init__(self):
        self._items: dict[int, Item] = {}
        self._session = MockSession()

    async def get(self, id: int) -> Item | None:
        return self._items.get(id)

    async def list(self, **filters) -> Sequence[Item]:
        if "universe_id" in filters:
            return [
                item for item in self._items.values() if item.universe_id == filters["universe_id"]
            ]
        return list(self._items.values())

    async def update_stock(self, item_id: int, new_stock: int) -> None:
        item = await self.get(item_id)
        if not item:
            raise ItemNotFoundException()
        self._items[item_id] = Item(
            id=item.id,
            name=item.name,
            universe_id=item.universe_id,
            price=item.price,
            stock=new_stock,
        )


class MockUniverseRepository(UniverseRepository):
    def __init__(self):
        self._universes: dict[int, Universe] = {}
        self._session = MockSession()

    async def get(self, id: int) -> Universe | None:
        return self._universes.get(id)

    async def list(self, **filters) -> Sequence[Universe]:
        return list(self._universes.values())


class MockTransactionRepository(TransactionRepository):
    def __init__(self):
        self._transactions: list[Transaction] = []
        self._session = MockSession()

    async def get(self, id: int) -> Transaction | None:
        for transaction in self._transactions:
            if transaction.id == id:
                return transaction
        return None

    async def list(self, **filters) -> Sequence[Transaction]:
        return self._transactions

    async def get_user_trades(self, user_id: int) -> Sequence[Transaction]:
        return [t for t in self._transactions if t.buyer_id == user_id]

    async def add(self, entity: Transaction) -> Transaction:
        if not isinstance(entity, Transaction):
            raise ValueError("Can only add Transaction entities")
        self._transactions.append(entity)
        return entity
