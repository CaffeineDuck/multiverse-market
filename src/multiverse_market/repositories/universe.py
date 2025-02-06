import logging
from sqlalchemy.ext.asyncio import AsyncSession

from .base import SQLAlchemyRepository
from ..models.entities import Universe

logger = logging.getLogger(__name__)

class UniverseRepository(SQLAlchemyRepository[Universe]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Universe)
        logger.debug("Initialized UniverseRepository") 