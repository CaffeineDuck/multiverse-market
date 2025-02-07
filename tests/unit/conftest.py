import pytest
import pytest_asyncio
import asyncio
from typing import Dict, List, Optional, Sequence, AsyncGenerator
from decimal import Decimal
from datetime import datetime

from multiverse_market.interfaces import CacheBackend
from multiverse_market.models.entities import User, Item, Universe, Transaction
from multiverse_market.models.schemas import UserSchema, ItemSchema, UniverseSchema, TransactionSchema
from multiverse_market.exceptions import (
    UserNotFoundException, ItemNotFoundException, UniverseNotFoundException,
    InsufficientBalanceException, InsufficientStockException
)
from tests.unit.mocks import (
    MockUserRepository, MockItemRepository, MockUniverseRepository, MockTransactionRepository,
    InMemoryCacheService
)

@pytest_asyncio.fixture
async def cache_backend() -> CacheBackend:
    return InMemoryCacheService()

@pytest_asyncio.fixture
async def user_repo() -> MockUserRepository:
    return MockUserRepository()

@pytest_asyncio.fixture
async def item_repo() -> MockItemRepository:
    return MockItemRepository()

@pytest_asyncio.fixture
async def universe_repo() -> MockUniverseRepository:
    return MockUniverseRepository()

@pytest_asyncio.fixture
async def transaction_repo() -> MockTransactionRepository:
    return MockTransactionRepository()

@pytest_asyncio.fixture
async def setup_test_data(
    user_repo: MockUserRepository,
    item_repo: MockItemRepository,
    universe_repo: MockUniverseRepository
) -> None:
    earth = Universe(id=1, name="Earth", currency_type="USD", exchange_rate=1.0)
    mars = Universe(id=2, name="Mars", currency_type="MRC", exchange_rate=2.5)
    universe_repo._universes[1] = earth
    universe_repo._universes[2] = mars
    
    user = User(id=1, username="test_user", universe_id=1, balance=1000.0)
    user_repo._users[1] = user
    
    item = Item(id=1, name="Test Item", universe_id=1, price=100.0, stock=10)
    item_repo._items[1] = item
    
    return None 