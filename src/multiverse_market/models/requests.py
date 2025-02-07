from pydantic import BaseModel


class CurrencyExchange(BaseModel):
    user_id: int
    amount: float
    from_universe_id: int
    to_universe_id: int


class ItemPurchase(BaseModel):
    buyer_id: int
    item_id: int
    quantity: int
