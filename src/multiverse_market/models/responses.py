from pydantic import BaseModel

class CurrencyExchangeResponse(BaseModel):
    """Response model for currency exchange operations."""
    converted_amount: float
    from_universe_id: int
    to_universe_id: int
    exchange_rate: float 