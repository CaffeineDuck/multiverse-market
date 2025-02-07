import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.entities import User
from .base import SQLAlchemyRepository

logger = logging.getLogger(__name__)


class UserRepository(SQLAlchemyRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
        logger.debug("Initialized UserRepository")

    async def update_balance(self, user_id: int, new_balance: float) -> None:
        user = await self.get(user_id)
        if user:
            logger.debug(
                f"Updating balance for user {user_id} from {user.balance} to {new_balance}"
            )
            user.balance = new_balance
            await self.update(user)
            logger.debug(f"Balance updated for user {user_id}")
        else:
            logger.warning(f"User {user_id} not found for balance update")
