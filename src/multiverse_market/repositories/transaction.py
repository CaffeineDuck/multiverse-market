import logging
import typing as ty
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import SQLAlchemyRepository
from ..models.entities import Transaction

logger = logging.getLogger(__name__)

class TransactionRepository(SQLAlchemyRepository[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)
    
    async def get_user_trades(self, user_id: int) -> ty.Sequence[Transaction]:
        logger.debug(f"Fetching trades for user {user_id}")
        result = await self._session.execute(
            select(Transaction)
            .where((Transaction.buyer_id == user_id) | (Transaction.seller_id == user_id))
            .order_by(Transaction.transaction_time.desc())
        )
        trades = result.scalars().all()
        logger.debug(f"Retrieved {len(trades)} trades for user {user_id}")
        return trades 