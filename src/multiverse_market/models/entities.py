from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Universe(Base):
    __tablename__ = "universes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    currency_type: Mapped[str]
    exchange_rate: Mapped[float]

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    universe_id: Mapped[int] = mapped_column(ForeignKey("universes.id"))
    balance: Mapped[float] = mapped_column(default=0.0)

class Item(Base):
    __tablename__ = "items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    universe_id: Mapped[int] = mapped_column(ForeignKey("universes.id"))
    price: Mapped[float]
    stock: Mapped[int]

class Transaction(Base):
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    from_universe_id: Mapped[int] = mapped_column(ForeignKey("universes.id"), nullable=False)
    to_universe_id: Mapped[int] = mapped_column(ForeignKey("universes.id"), nullable=False)
    transaction_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow) 