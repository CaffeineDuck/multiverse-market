import logging
import random
import time
import typing as ty
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Union

from locust import HttpUser, LoadTestShape, between, events, stats, task
from locust.clients import ResponseContextManager
from locust.contrib.fasthttp import FastHttpUser
from requests import Response
from locust.clients import LocustResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATS_INTERVAL_SEC: ty.Final[int] = 1
STATS_FLUSH_INTERVAL_SEC: ty.Final[int] = 10
MAX_ERRORS: ty.Final[int] = 5
MAX_RETRIES: ty.Final[int] = 3
INITIAL_RETRY_WAIT: ty.Final[int] = 1

stats.CSV_STATS_INTERVAL_SEC = STATS_INTERVAL_SEC
stats.CSV_STATS_FLUSH_INTERVAL_SEC = STATS_FLUSH_INTERVAL_SEC


@dataclass
class LoadStage:
    duration: int
    users: int
    spawn_rate: int


@dataclass
class ItemData:
    stock: float
    price: float
    universe_id: int


@dataclass
class UserSession:
    start_time: datetime = field(default_factory=datetime.now)
    errors: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    trade_history: list[dict] = field(default_factory=list)
    user_balances: dict[int, float] = field(default_factory=dict)
    item_stocks: dict[int, ItemData] = field(default_factory=dict)


class LoadTestConfig:
    USER_IDS: ty.Final[list[int]] = [1, 2, 3]
    UNIVERSE_IDS: ty.Final[list[int]] = [1, 2, 3]
    ITEM_IDS: ty.Final[list[int]] = [1, 2, 3]

    HEALTH_CHECK: ty.Final[str] = "/health"
    UNIVERSES: ty.Final[str] = "/api/v1/universes"
    ITEMS: ty.Final[str] = "/api/v1/items"
    USERS: ty.Final[str] = "/api/v1/users"
    TRADES: ty.Final[str] = "/api/v1/trades"
    EXCHANGE: ty.Final[str] = "/api/v1/exchange"
    BUY: ty.Final[str] = "/api/v1/buy"


class StagesLoadShape(LoadTestShape):
    """
    Defines a multi-stage load test pattern with warm-up, steady state,
    spike, and cool-down phases.
    """

    stages: ClassVar[list[LoadStage]] = [
        LoadStage(duration=60, users=10, spawn_rate=1),  # Warm-up
        LoadStage(duration=180, users=50, spawn_rate=2),  # Steady state
        LoadStage(duration=120, users=100, spawn_rate=5),  # Spike
        LoadStage(duration=60, users=10, spawn_rate=1),  # Cool-down
    ]

    def tick(self) -> tuple[int, float] | None:
        """Calculate the target user count and spawn rate for the current time."""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage.duration:
                return (stage.users, stage.spawn_rate)
            run_time -= stage.duration
        return None


class BaseUser(HttpUser):
    """Base user class with common functionality for all user types."""

    abstract = True
    wait_time = between(1, 3)

    def __init__(self, *args: ty.Any, **kwargs: ty.Any) -> None:
        super().__init__(*args, **kwargs)
        self.session = UserSession()

    def handle_response(self, response: Union[ResponseContextManager, Response, LocustResponse], context: str) -> bool:
        """
        Common response handling with error tracking.

        Args:
            response: The response from the API (can be various response types)
            context: Description of the current operation

        Returns:
            bool: True if the response was successful, False otherwise
        """
        if response.status_code >= 400:
            self.session.errors += 1
            logger.error(f"Error in {context}: {response.status_code} - {response.text}")

            if isinstance(response, ResponseContextManager):
                response.failure(f"{context} failed: {response.status_code}")

            if self.session.errors >= MAX_ERRORS:
                logger.error(f"User exceeded maximum errors ({MAX_ERRORS}), stopping")
                self.environment.runner.quit()
            return False

        self.session.errors = max(0, self.session.errors - 1)
        if isinstance(response, ResponseContextManager):
            response.success()
        return True

    def retry_with_backoff[T](self, func: ty.Callable[[], T]) -> T:
        """
        Enhanced retry mechanism with health checks and logging.

        Args:
            func: The function to retry

        Returns:
            The result of the function call

        Raises:
            Exception: If all retries fail
        """
        for attempt in range(MAX_RETRIES):
            try:
                with self.client.get(
                    LoadTestConfig.HEALTH_CHECK, catch_response=True
                ) as health_check:
                    if health_check.status_code != 200:
                        logger.warning("Health check failed, waiting before retry")
                        time.sleep(INITIAL_RETRY_WAIT * (2**attempt))
                        continue

                return func()
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Max retries reached: {e!s}")
                    raise e
                wait_time = INITIAL_RETRY_WAIT * (2**attempt)
                logger.warning(f"Attempt {attempt + 1} failed, waiting {wait_time}s: {e!s}")
                time.sleep(wait_time)
        # Should be unreachable
        raise Exception("max retries reached")


class BrowserUser(BaseUser):
    """Simulates users browsing the marketplace."""

    weight = 70  # 70% of users will be browsers

    @task(4)
    def list_universes(self) -> None:
        """List all universes - high frequency task."""
        with self.client.get(
            LoadTestConfig.UNIVERSES, catch_response=True, name="List Universes"
        ) as response:
            if self.handle_response(response, "list_universes"):
                self.universes = response.json()

    @task(5)
    def list_items(self) -> None:
        """List items with universe filtering."""
        if random.choice([True, False]):
            universe_id = random.choice(LoadTestConfig.UNIVERSE_IDS)
            endpoint = f"{LoadTestConfig.ITEMS}?universe_id={universe_id}"
            name = "List Items By Universe"
        else:
            endpoint = LoadTestConfig.ITEMS
            name = "List All Items"

        with self.client.get(endpoint, catch_response=True, name=name) as response:
            if self.handle_response(response, f"list_items ({name})"):
                items = response.json()
                for item in items:
                    self.session.item_stocks[item["id"]] = ItemData(
                        stock=item["stock"], price=item["price"], universe_id=item["universe_id"]
                    )

    @task(2)
    def get_user(self) -> None:
        """Get user details."""
        user_id = random.choice(LoadTestConfig.USER_IDS)
        with self.client.get(
            f"{LoadTestConfig.USERS}/{user_id}", catch_response=True, name="Get User"
        ) as response:
            if self.handle_response(response, "get_user"):
                user_data = response.json()
                self.session.user_balances[user_id] = user_data["balance"]


class TraderUser(BaseUser):
    """Simulates active traders making transactions."""

    weight = 30  # 30% of users will be traders
    wait_time = between(3, 7)  # Traders take more time between actions

    @task(2)
    def get_user_trades(self) -> None:
        """Get user trade history."""
        user_id = random.choice(LoadTestConfig.USER_IDS)
        with self.client.get(
            f"{LoadTestConfig.TRADES}/{user_id}", catch_response=True, name="Get User Trades"
        ) as response:
            if self.handle_response(response, "get_user_trades"):
                self.session.trade_history = response.json()

    @task(1)
    def exchange_currency(self) -> None:
        """Attempt to exchange currency between universes."""

        def do_exchange() -> Union[ResponseContextManager, Response, LocustResponse, None]:
            user_id = random.choice(LoadTestConfig.USER_IDS)

            # Update balance before exchange
            with self.client.get(
                f"{LoadTestConfig.USERS}/{user_id}", catch_response=True, name="Get User Balance"
            ) as response:
                if not self.handle_response(response, "get_user_balance"):
                    return None
                user_data = response.json()
                self.session.user_balances[user_id] = user_data["balance"]

            if (
                user_id not in self.session.user_balances
                or self.session.user_balances[user_id] <= 0
            ):
                return None

            max_amount = self.session.user_balances[user_id] * 0.5
            from_universe = random.choice(LoadTestConfig.UNIVERSE_IDS)
            to_universe = random.choice(
                [u for u in LoadTestConfig.UNIVERSE_IDS if u != from_universe]
            )

            exchange_data = {
                "user_id": user_id,
                "amount": random.uniform(10.0, min(100.0, max_amount)),
                "from_universe_id": from_universe,
                "to_universe_id": to_universe,
            }

            with self.client.post(
                LoadTestConfig.EXCHANGE,
                json=exchange_data,
                catch_response=True,
                name="Exchange Currency",
            ) as response:
                if self.handle_response(response, "exchange_currency"):
                    self.session.successful_trades += 1
                else:
                    self.session.failed_trades += 1
                return response

        self.retry_with_backoff(do_exchange)

    @task(1)
    def buy_item(self) -> None:
        """Attempt to purchase an item."""

        def do_purchase() -> Union[ResponseContextManager, Response, LocustResponse, None]:
            buyer_id = random.choice(LoadTestConfig.USER_IDS)

            # Update user balance
            with self.client.get(
                f"{LoadTestConfig.USERS}/{buyer_id}", catch_response=True, name="Get Buyer Balance"
            ) as response:
                if not self.handle_response(response, "get_buyer_balance"):
                    return None
                user_data = response.json()
                self.session.user_balances[buyer_id] = user_data["balance"]

            if buyer_id not in self.session.user_balances:
                return None

            # Get available items
            with self.client.get(
                LoadTestConfig.ITEMS, catch_response=True, name="List Available Items"
            ) as response:
                if not self.handle_response(response, "list_available_items"):
                    return None
                items = response.json()
                for item in items:
                    self.session.item_stocks[item["id"]] = ItemData(
                        stock=item["stock"], price=item["price"], universe_id=item["universe_id"]
                    )

            available_items = [
                (item_id, data)
                for item_id, data in self.session.item_stocks.items()
                if data.stock > 0
            ]

            if not available_items:
                return None

            item_id, item_data = random.choice(available_items)
            max_quantity = min(3, int(item_data.stock))

            if max_quantity <= 0:
                return None

            quantity = random.randint(1, max_quantity)
            total_cost = quantity * item_data.price

            if self.session.user_balances[buyer_id] < total_cost:
                return None

            purchase_data = {"buyer_id": buyer_id, "item_id": item_id, "quantity": quantity}

            with self.client.post(
                LoadTestConfig.BUY, json=purchase_data, catch_response=True, name="Buy Item"
            ) as response:
                if self.handle_response(response, "buy_item"):
                    self.session.successful_trades += 1
                    # Update cached data
                    self.session.item_stocks[item_id].stock -= quantity
                    self.session.user_balances[buyer_id] -= total_cost
                else:
                    self.session.failed_trades += 1
                return response

        self.retry_with_backoff(do_purchase)


# Event handlers for test-wide metrics
@events.test_start.add_listener
def on_test_start(**kwargs: dict[str, ty.Any]) -> None:
    """Log test start and initialize any necessary resources."""
    logger.info("Load test starting")


@events.test_stop.add_listener
def on_test_stop(**kwargs: dict[str, ty.Any]) -> None:
    """Log test completion and cleanup any resources."""
    logger.info("Load test completed")


@events.request.add_listener
def on_request(
    request_type: str,
    name: str,
    response_time: float,
    response_length: int,
    exception: Exception | None,
    **kwargs: dict[str, ty.Any],
) -> None:
    """Log failed requests with details."""
    if exception:
        logger.error(f"Request failed: {name} - {exception!s}")


@dataclass(frozen=True)
class UniverseData:
    id: int
    name: str
    currency_type: str
    exchange_rate: float


class MarketUser(HttpUser):
    """Market user class for load testing."""

    universes: ClassVar[list[UniverseData]] = [
        UniverseData(id=1, name="Earth Prime", currency_type="USD", exchange_rate=1.0),
        UniverseData(id=2, name="Mars Colony", currency_type="MC", exchange_rate=0.75),
        UniverseData(id=3, name="Luna Base", currency_type="LUN", exchange_rate=1.25),
    ]
