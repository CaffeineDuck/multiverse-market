import logging
from collections.abc import Sequence
from typing import Generic, Optional, Protocol, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.entities import Base

T = TypeVar("T")

logger = logging.getLogger(__name__)


class Repository(Protocol[T]):
    """Base repository protocol."""

    async def get(self, id: int) -> T | None:
        """Get entity by ID."""
        ...

    async def list(self, **filters) -> Sequence[T]:
        """List entities with optional filters."""
        ...

    async def add(self, entity: T) -> T:
        """Add new entity."""
        ...

    async def update(self, entity: T) -> T:
        """Update existing entity."""
        ...

    async def delete(self, id: int) -> None:
        """Delete entity by ID."""
        ...


class SQLAlchemyRepository(Generic[T]):
    """Base SQLAlchemy repository implementation."""

    def __init__(self, session: AsyncSession, model: type[T]):
        logger.debug(f"Initializing {self.__class__.__name__}")
        self._session = session
        self._model = model

    async def get(self, id: int) -> T | None:
        logger.debug(f"Getting {self._model.__name__} with id {id}")
        result = await self._session.execute(select(self._model).where(self._model.id == id))
        entity = result.scalar_one_or_none()
        if entity is None:
            logger.debug(f"{self._model.__name__} with id {id} not found")
        return entity

    async def list(self, **filters) -> Sequence[T]:
        logger.debug(f"Listing {self._model.__name__} with filters: {filters}")
        query = select(self._model)
        for key, value in filters.items():
            if value is not None:
                query = query.where(getattr(self._model, key) == value)
        result = await self._session.execute(query)
        entities = result.scalars().all()
        logger.debug(f"Found {len(entities)} {self._model.__name__} records")
        return entities

    async def add(self, entity: T) -> T:
        logger.debug(f"Adding new {self._model.__name__}")
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        logger.debug(f"Added {self._model.__name__} with id {entity.id}")
        return entity

    async def update(self, entity: T) -> T:
        logger.debug(f"Updating {self._model.__name__} with id {entity.id}")
        await self._session.commit()
        await self._session.refresh(entity)
        logger.debug(f"Updated {self._model.__name__} with id {entity.id}")
        return entity

    async def delete(self, id: int) -> None:
        logger.debug(f"Deleting {self._model.__name__} with id {id}")
        entity = await self.get(id)
        if entity:
            await self._session.delete(entity)
            await self._session.commit()
            logger.debug(f"Deleted {self._model.__name__} with id {id}")
        else:
            logger.warning(f"{self._model.__name__} with id {id} not found for deletion")
