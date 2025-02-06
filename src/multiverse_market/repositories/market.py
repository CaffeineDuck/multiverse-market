from sqlalchemy import select
import typing as ty
from sqlalchemy.ext.asyncio import AsyncSession

from .base import SQLAlchemyRepository
from ..models.entities import User, Item, Transaction, Universe

class UserRepository(SQLAlchemyRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def update_balance(self, user_id: int, new_balance: float) -> None:
        user = await self.get(user_id)
        if user:
            user.balance = new_balance
            await self.update(user)

class ItemRepository(SQLAlchemyRepository[Item]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Item)
    
    async def update_stock(self, item_id: int, new_stock: int) -> None:
        item = await self.get(item_id)
        if item:
            item.stock = new_stock
            await self.update(item)

class TransactionRepository(SQLAlchemyRepository[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)
    
    async def get_user_trades(self, user_id: int) -> ty.Sequence[Transaction]:
        result = await self._session.execute(
            select(Transaction)
            .where((Transaction.buyer_id == user_id) | (Transaction.seller_id == user_id))
            .order_by(Transaction.transaction_time.desc())
        )
        return result.scalars().all()

class UniverseRepository(SQLAlchemyRepository[Universe]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Universe) 