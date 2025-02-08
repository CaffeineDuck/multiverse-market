import logging

import pytest
import pytest_asyncio

from multiverse_market.exceptions import (
    InsufficientBalanceException,
    InsufficientStockException,
    ItemNotFoundException,
    UniverseNotFoundException,
    UserNotFoundException,
)
from multiverse_market.interfaces import CacheBackend
from multiverse_market.models.entities import Item
from multiverse_market.models.requests import CurrencyExchange, ItemPurchase
from multiverse_market.services.market import MarketService
from tests.unit.mocks import (
    MockItemRepository,
    MockTransactionRepository,
    MockUniverseRepository,
    MockUserRepository,
)

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def market_service(
    cache_backend: CacheBackend,
    user_repo: MockUserRepository,
    item_repo: MockItemRepository,
    universe_repo: MockUniverseRepository,
    transaction_repo: MockTransactionRepository,
    setup_test_data: None,
) -> MarketService:
    logger.debug("Creating market service with repositories")
    service = MarketService(
        user_repo=user_repo,
        item_repo=item_repo,
        transaction_repo=transaction_repo,
        universe_repo=universe_repo,
        cache=cache_backend,
    )
    logger.debug(f"Created market service with item_repo: {item_repo._items}")
    return service


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.service
class TestMarketService:
    @pytest.mark.currency
    async def test_exchange_currency_success(
        self, market_service: MarketService, user_repo: MockUserRepository, setup_test_data: None
    ) -> None:
        """Test successful currency exchange between universes."""
        exchange = CurrencyExchange(user_id=1, amount=100.0, from_universe_id=1, to_universe_id=2)

        logger.debug(
            f"Exchange details: {exchange.amount} from universe {exchange.from_universe_id} "
            f"to {exchange.to_universe_id}"
        )

        result = await market_service.exchange_currency(exchange)

        assert result.converted_amount == 250.0  # 100 * (2.5/1.0)
        assert result.exchange_rate == 2.5
        user = await user_repo.get(1)
        if user is None:
            raise Exception("user not found")
        assert user.balance == 900.0  # 1000 - 100

    @pytest.mark.currency
    async def test_exchange_currency_insufficient_balance(
        self, market_service: MarketService, setup_test_data: None
    ) -> None:
        """Test currency exchange fails with insufficient balance."""
        exchange = CurrencyExchange(user_id=1, amount=2000.0, from_universe_id=1, to_universe_id=2)

        with pytest.raises(InsufficientBalanceException):
            await market_service.exchange_currency(exchange)

    @pytest.mark.currency
    async def test_exchange_currency_invalid_user(
        self, market_service: MarketService, setup_test_data: None
    ) -> None:
        """Test currency exchange fails with invalid user."""
        exchange = CurrencyExchange(user_id=999, amount=100.0, from_universe_id=1, to_universe_id=2)

        with pytest.raises(UserNotFoundException):
            await market_service.exchange_currency(exchange)

    @pytest.mark.currency
    async def test_exchange_currency_invalid_universe(
        self, market_service: MarketService, setup_test_data: None
    ) -> None:
        """Test currency exchange fails with invalid universe."""
        exchange = CurrencyExchange(user_id=1, amount=100.0, from_universe_id=999, to_universe_id=2)

        with pytest.raises(UniverseNotFoundException):
            await market_service.exchange_currency(exchange)

    @pytest.mark.currency
    async def test_exchange_currency_between_same_universe(
        self, market_service: MarketService, setup_test_data: None
    ) -> None:
        """Test that exchanging currency within same universe raises error."""
        exchange = CurrencyExchange(user_id=1, amount=100.0, from_universe_id=1, to_universe_id=1)

        with pytest.raises(ValueError):
            await market_service.exchange_currency(exchange)

    @pytest.mark.purchase
    async def test_buy_item_success(
        self,
        market_service: MarketService,
        user_repo: MockUserRepository,
        item_repo: MockItemRepository,
        setup_test_data: None,
    ) -> None:
        """Test successful item purchase."""
        purchase = ItemPurchase(buyer_id=1, item_id=1, quantity=2)

        result = await market_service.buy_item(purchase)

        assert result.buyer_id == 1
        assert result.quantity == 2
        assert result.amount == 200.0

        user = await user_repo.get(1)
        if user is None:
            raise Exception("user not found")
        assert user.balance == 800.0  # 1000 - (100 * 2)

        item = await item_repo.get(1)
        if item is None:
            raise Exception("item not found")
        assert item.stock == 8  # 10 - 2

    @pytest.mark.purchase
    async def test_buy_item_insufficient_stock(
        self, market_service: MarketService, setup_test_data: None
    ) -> None:
        """Test item purchase fails with insufficient stock."""
        purchase = ItemPurchase(buyer_id=1, item_id=1, quantity=20)

        with pytest.raises(InsufficientStockException):
            await market_service.buy_item(purchase)

    @pytest.mark.purchase
    async def test_buy_item_invalid_item(
        self, market_service: MarketService, setup_test_data: None
    ) -> None:
        """Test item purchase fails with invalid item."""
        purchase = ItemPurchase(buyer_id=1, item_id=999, quantity=1)

        with pytest.raises(ItemNotFoundException):
            await market_service.buy_item(purchase)

    @pytest.mark.purchase
    async def test_buy_item_invalid_buyer(
        self, market_service: MarketService, setup_test_data: None
    ) -> None:
        """Test item purchase fails with invalid buyer."""
        purchase = ItemPurchase(buyer_id=999, item_id=1, quantity=1)

        with pytest.raises(UserNotFoundException):
            await market_service.buy_item(purchase)

    @pytest.mark.purchase
    async def test_buy_item_cross_universe_insufficient_balance(
        self,
        market_service: MarketService,
        item_repo: MockItemRepository,
        setup_test_data: None,
    ) -> None:
        """Test item purchase fails when buying from different universe with
        insufficient balance."""
        # Add a more expensive Mars item
        mars_item = Item(
            id=3,
            name="Mars Item",
            universe_id=2,
            price=300.0,
            stock=5,
        )
        item_repo._items[3] = mars_item

        # User from Earth (rate 1.0) trying to buy Mars item (rate 2.5)
        purchase = ItemPurchase(buyer_id=1, item_id=3, quantity=2)

        with pytest.raises(InsufficientBalanceException):
            await market_service.buy_item(purchase)

    @pytest.mark.user
    async def test_get_user_not_found(self, market_service: MarketService) -> None:
        """Test user retrieval fails for non-existent user."""
        with pytest.raises(UserNotFoundException):
            await market_service.get_user(999)

    @pytest.mark.item
    async def test_list_items_with_universe_filter(
        self,
        market_service: MarketService,
        item_repo: MockItemRepository,
        setup_test_data: None,
    ) -> None:
        """Test item listing with universe filter."""
        # Create a Mars item for testing
        item2 = Item(
            id=2,
            name="Mars Item",
            universe_id=2,
            price=200.0,
            stock=5,
        )
        item_repo._items[2] = item2

        # Get items from Earth (universe_id=1)
        result = await market_service.list_items(universe_id=1)

        # Verify only Earth items are returned
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Test Item"
        assert result[0].universe_id == 1

    @pytest.mark.purchase
    async def test_buy_item_updates_transaction_history(
        self,
        market_service: MarketService,
        transaction_repo: MockTransactionRepository,
        setup_test_data: None,
    ) -> None:
        """Test that buying an item creates a transaction record."""
        purchase = ItemPurchase(buyer_id=1, item_id=1, quantity=1)

        await market_service.buy_item(purchase)

        trades = await transaction_repo.get_user_trades(1)
        assert len(trades) == 1
        assert trades[0].buyer_id == 1
        assert trades[0].item_id == 1
        assert trades[0].quantity == 1
        assert trades[0].amount == 100.0

    @pytest.mark.cache
    async def test_exchange_rate_caching(
        self, market_service: MarketService, cache_backend: CacheBackend, setup_test_data: None
    ) -> None:
        """Test that exchange rates are properly cached."""
        exchange = CurrencyExchange(user_id=1, amount=100.0, from_universe_id=1, to_universe_id=2)

        # First call should cache the rate
        result1 = await market_service.exchange_currency(exchange)

        # Second call should use cached rate
        result2 = await market_service.exchange_currency(exchange)

        assert result1.exchange_rate == result2.exchange_rate
        assert result1.converted_amount == result2.converted_amount

    @pytest.mark.cache
    async def test_exchange_rate_cache_invalidation(
        self, market_service: MarketService, cache_backend: CacheBackend, setup_test_data: None
    ) -> None:
        """Test that exchange rate caches are properly invalidated."""
        # First, make an exchange to cache the rate
        exchange = CurrencyExchange(user_id=1, amount=100.0, from_universe_id=1, to_universe_id=2)
        await market_service.exchange_currency(exchange)

        # Verify rate is cached
        cache_key = "exchange_rate:1:2"
        assert await cache_backend.get(cache_key) is not None

        # Invalidate cache for universe 1
        await market_service._invalidate_exchange_rate_cache(1)

        # Verify cache is cleared
        assert await cache_backend.get(cache_key) is None
        assert await cache_backend.get("exchange_rate:2:1") is None

    @pytest.mark.item
    async def test_list_items_without_universe_filter(
        self,
        market_service: MarketService,
        item_repo: MockItemRepository,
        setup_test_data: None,
    ) -> None:
        """Test listing all items without universe filter."""
        logger.debug("Starting test_list_items_without_universe_filter")
        logger.debug(f"Initial items in repo: {item_repo._items}")

        # Get initial items (should be one from setup_test_data)
        initial_items = await market_service.list_items()
        logger.debug(f"Initial items from list_items: {initial_items}")
        assert len(initial_items) == 1
        assert initial_items[0].name == "Test Item"
        assert initial_items[0].universe_id == 1

        # Add item from Mars (universe_id=2)
        mars_item = Item(
            id=2,  # Use id=2 since id=1 is already used in setup_test_data
            name="Mars Item",
            universe_id=2,
            price=200.0,
            stock=5,
        )
        item_repo._items[2] = mars_item
        logger.debug(f"Added Mars item, current items: {item_repo._items}")

        # Get all items
        result = await market_service.list_items()
        logger.debug(f"Final items from list_items: {result}")

        # Verify all items are returned
        assert len(result) == 2
        assert {item.universe_id for item in result} == {1, 2}
        assert {item.name for item in result} == {"Test Item", "Mars Item"}

    @pytest.mark.cache
    async def test_item_cache_validation(
        self,
        market_service: MarketService,
        item_repo: MockItemRepository,
        cache_backend: CacheBackend,
        setup_test_data: None,
    ) -> None:
        """Test that item cache is validated and updated when item details change."""
        # Make a purchase to cache the item
        purchase = ItemPurchase(buyer_id=1, item_id=1, quantity=1)
        await market_service.buy_item(purchase)

        # Manually modify the item in the repository
        item = item_repo._items[1]
        item.price = 150.0  # Change price
        item_repo._items[1] = item

        # Make another purchase - should detect cache mismatch and update
        purchase = ItemPurchase(buyer_id=1, item_id=1, quantity=1)
        result = await market_service.buy_item(purchase)

        # Verify the new price was used
        assert result.amount == 150.0

    @pytest.mark.transaction
    async def test_get_user_trades(
        self,
        market_service: MarketService,
        transaction_repo: MockTransactionRepository,
        setup_test_data: None,
    ) -> None:
        """Test retrieving user trade history."""
        # Make multiple purchases
        purchase1 = ItemPurchase(buyer_id=1, item_id=1, quantity=1)
        purchase2 = ItemPurchase(buyer_id=1, item_id=1, quantity=2)

        await market_service.buy_item(purchase1)
        await market_service.buy_item(purchase2)

        # Get trade history
        trades = await market_service.get_user_trades(1)

        # Verify all trades are returned
        assert len(trades) == 2
        assert trades[0].quantity == 1
        assert trades[1].quantity == 2
        assert all(trade.buyer_id == 1 for trade in trades)
