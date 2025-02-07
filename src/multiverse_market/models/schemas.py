from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UniverseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str
    currency_type: str
    exchange_rate: float


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    username: str
    universe_id: int
    balance: float


class ItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str
    universe_id: int
    price: float
    stock: int


class TransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    buyer_id: int
    seller_id: int
    item_id: int
    amount: float
    quantity: int
    from_universe_id: int
    to_universe_id: int
    transaction_time: datetime | None = None
