from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel

class Base(DeclarativeBase):
    pass

# Database Models
class UniverseDB(Base):
    __tablename__ = "universes"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    currency_type = Column(String, nullable=False)
    exchange_rate = Column(Float, nullable=False)

class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    universe_id = Column(Integer, ForeignKey("universes.id"), nullable=False)
    balance = Column(Float, default=0.0)

class ItemDB(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    universe_id = Column(Integer, ForeignKey("universes.id"), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)

class TransactionDB(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    amount = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    from_universe_id = Column(Integer, ForeignKey("universes.id"), nullable=False)
    to_universe_id = Column(Integer, ForeignKey("universes.id"), nullable=False)
    transaction_time = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class UniverseSchema(BaseModel):
    id: Optional[int] = None
    name: str
    currency_type: str
    exchange_rate: float

    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    id: Optional[int] = None
    username: str
    universe_id: int
    balance: float

    class Config:
        from_attributes = True

class ItemSchema(BaseModel):
    id: Optional[int] = None
    name: str
    universe_id: int
    price: float
    stock: int

    class Config:
        from_attributes = True

class TransactionSchema(BaseModel):
    id: Optional[int] = None
    buyer_id: int
    seller_id: int
    item_id: int
    amount: float
    quantity: int
    from_universe_id: int
    to_universe_id: int
    transaction_time: Optional[datetime] = None

    class Config:
        from_attributes = True

# Request/Response Models
class CurrencyExchange(BaseModel):
    user_id: int
    amount: float
    from_universe_id: int
    to_universe_id: int

class ItemPurchase(BaseModel):
    buyer_id: int
    item_id: int
    quantity: int 