import pytest

from multiverse_market.exceptions import (
    InsufficientBalanceException,
    InsufficientStockException,
    ItemNotFoundException,
    UniverseNotFoundException,
    UserNotFoundException,
)
from multiverse_market.interfaces import CacheBackend
from multiverse_market.models.entities import Item, Universe, User
from multiverse_market.models.requests import CurrencyExchange, ItemPurchase
from multiverse_market.services.market import MarketService
from tests.unit.mocks import (
    MockItemRepository,
    MockTransactionRepository,
    MockUniverseRepository,
    MockUserRepository,
)


@pytest.fixture
def market_service(
    cache_backend: CacheBackend,
    user_repo: MockUserRepository,
    item_repo: MockItemRepository,
    universe_repo: MockUniverseRepository,
    transaction_repo: MockTransactionRepository,
) -> MarketService:
    return MarketService(
        user_repo=user_repo,
        item_repo=item_repo,
        transaction_repo=transaction_repo,
        universe_repo=universe_repo,
        cache=cache_backend,
    )


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
        assert user.balance == 800.0  # 1000 - (100 * 2)

        item = await item_repo.get(1)
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
    async def test_item_cache_invalidation(
        self, market_service: MarketService, cache_backend: CacheBackend, setup_test_data: None
    ) -> None:
        """Test that item cache is invalidated after purchase."""
        purchase = ItemPurchase(buyer_id=1, item_id=1, quantity=1)

        # Make a purchase which should cache the item
        await market_service.buy_item(purchase)

        # Verify that the cache was invalidated
        cached_item = await cache_backend.get("item:1")
        assert cached_item is None
