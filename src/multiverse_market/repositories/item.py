import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.entities import Item
from .base import SQLAlchemyRepository

logger = logging.getLogger(__name__)


class ItemRepository(SQLAlchemyRepository[Item]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Item)

    async def update_stock(self, item_id: int, new_stock: int) -> None:
        item = await self.get(item_id)
        if item:
            logger.debug(f"Updating stock for item {item_id} from {item.stock} to {new_stock}")
            item.stock = new_stock
            await self.update(item)
            logger.debug(f"Stock updated for item {item_id}")
        else:
            logger.warning(f"Item {item_id} not found for stock update")
