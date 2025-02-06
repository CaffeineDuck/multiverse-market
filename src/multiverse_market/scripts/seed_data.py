"""Script to seed test data into the database."""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.entities import Universe, User, Item
from ..dependencies import async_session

async def seed_data(session: AsyncSession) -> None:
    """Seed test data into the database."""
    # Create universes
    universes = [
        Universe(id=1, name='Earth', currency_type='USD', exchange_rate=1.0),
        Universe(id=2, name='Mars', currency_type='MRC', exchange_rate=2.5),
        Universe(id=3, name='Venus', currency_type='VNC', exchange_rate=0.75)
    ]
    for universe in universes:
        session.add(universe)
    await session.commit()

    # Create users
    users = [
        User(id=1, username='john_earth', universe_id=1, balance=1000.0),
        User(id=2, username='mary_mars', universe_id=2, balance=2500.0),
        User(id=3, username='venus_trader', universe_id=3, balance=750.0)
    ]
    for user in users:
        session.add(user)
    await session.commit()

    # Create items
    items = [
        Item(id=1, name='Earth Coffee', universe_id=1, price=5.0, stock=100),
        Item(id=2, name='Mars Rocks', universe_id=2, price=10.0, stock=50),
        Item(id=3, name='Venus Crystals', universe_id=3, price=15.0, stock=25)
    ]
    for item in items:
        session.add(item)
    await session.commit()

async def main() -> None:
    """Main entry point for seeding data."""
    async with async_session() as session:
        await seed_data(session)

if __name__ == '__main__':
    asyncio.run(main()) 