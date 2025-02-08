"""Integration tests for the API endpoints."""
import logging

import pytest
from httpx import AsyncClient

from multiverse_market.models.requests import CurrencyExchange, ItemPurchase

logger = logging.getLogger(__name__)


@pytest.mark.integration
class TestAPI:
    @pytest.mark.asyncio
    async def test_health_check(self, test_app: AsyncClient, setup_test_data: None):
        """Test the health check endpoint."""
        response = await test_app.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @pytest.mark.asyncio
    async def test_list_universes(self, test_app: AsyncClient, setup_test_data: None):
        """Test listing universes."""
        response = await test_app.get("/api/v1/universes")
        assert response.status_code == 200
        universes = response.json()
        assert len(universes) == 2
        assert {u["name"] for u in universes} == {"Earth", "Mars"}
        assert {u["currency_type"] for u in universes} == {"USD", "MRC"}

    @pytest.mark.asyncio
    async def test_list_items(self, test_app: AsyncClient, setup_test_data: None):
        """Test listing items."""
        # Test listing all items
        response = await test_app.get("/api/v1/items")
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 2
        assert {item["name"] for item in items} == {"Earth Item", "Mars Item"}

        # Test listing items by universe
        response = await test_app.get("/api/v1/items", params={"universe_id": 1})
        assert response.status_code == 200
        universe_items = response.json()
        assert len(universe_items) == 1
        assert universe_items[0]["name"] == "Earth Item"
        assert universe_items[0]["universe_id"] == 1

    @pytest.mark.asyncio
    async def test_get_user(self, test_app: AsyncClient, setup_test_data: None):
        """Test getting user details."""
        # Test getting an existing user
        response = await test_app.get("/api/v1/users/1")
        assert response.status_code == 200
        user = response.json()
        assert user["username"] == "test_user"
        assert user["balance"] == 1000.0

        # Test getting a non-existent user
        response = await test_app.get("/api/v1/users/999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_exchange_currency(self, test_app: AsyncClient, setup_test_data: None):
        """Test currency exchange."""
        exchange_data = CurrencyExchange(
            user_id=1,
            from_universe_id=1,
            to_universe_id=2,
            amount=100.0
        ).model_dump()
        response = await test_app.post("/api/v1/exchange", json=exchange_data)
        assert response.status_code == 200
        result = response.json()
        assert result["converted_amount"] == 250.0  # 100 * (2.5/1.0)
        assert result["exchange_rate"] == 2.5

    @pytest.mark.asyncio
    async def test_buy_item(self, test_app: AsyncClient, setup_test_data: None):
        """Test buying an item."""
        purchase_data = ItemPurchase(
            buyer_id=1,
            item_id=1,
            quantity=1
        ).model_dump()
        response = await test_app.post("/api/v1/buy", json=purchase_data)
        assert response.status_code == 200
        result = response.json()
        assert result["id"] is not None
        assert result["buyer_id"] == 1
        assert result["item_id"] == 1
        assert result["quantity"] == 1
        assert result["amount"] == 100.0  # price * quantity
        assert result["from_universe_id"] == 1
        assert result["to_universe_id"] == 1
        assert result["transaction_time"] is not None

    @pytest.mark.asyncio
    async def test_get_user_trades(self, test_app: AsyncClient, setup_test_data: None):
        """Test getting user trades."""
        # First make a purchase to create a trade
        purchase_data = ItemPurchase(
            buyer_id=1,
            item_id=1,
            quantity=1
        ).model_dump()
        response = await test_app.post("/api/v1/buy", json=purchase_data)
        assert response.status_code == 200

        # Test getting trades
        response = await test_app.get("/api/v1/users/1/trades")
        assert response.status_code == 200
        trades = response.json()
        assert len(trades) == 1
        trade = trades[0]
        assert trade["buyer_id"] == 1
        assert trade["item_id"] == 1
        assert trade["quantity"] == 1
        assert trade["amount"] == 100.0

    @pytest.mark.asyncio
    async def test_error_responses(self, test_app: AsyncClient, setup_test_data: None):
        """Test error responses."""
        # Test invalid universe ID
        response = await test_app.get("/api/v1/items", params={"universe_id": 999})
        assert response.status_code == 404
        assert "Universe not found" in response.json()["detail"]

        # Test invalid user ID
        response = await test_app.get("/api/v1/users/999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

        # Test invalid user trades
        response = await test_app.get("/api/v1/users/999/trades")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"] 