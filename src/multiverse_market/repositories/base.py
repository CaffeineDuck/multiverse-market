from typing import Protocol, TypeVar, Generic, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.entities import Base

T = TypeVar('T')

class Repository(Protocol[T]):
    """Base repository protocol."""
    async def get(self, id: int) -> Optional[T]:
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
        self._session = session
        self._model = model

    async def get(self, id: int) -> Optional[T]:
        result = await self._session.execute(
            select(self._model).where(self._model.id == id)
        )
        return result.scalar_one_or_none()

    async def list(self, **filters) -> Sequence[T]:
        query = select(self._model)
        for key, value in filters.items():
            if value is not None:
                query = query.where(getattr(self._model, key) == value)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def add(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def delete(self, id: int) -> None:
        entity = await self.get(id)
        if entity:
            await self._session.delete(entity)
            await self._session.commit() 