"""Command line interface for multiverse market."""

import asyncio
import logging
from pathlib import Path

import typer

from .dependencies import async_session
from .scripts.seed_data import seed_data

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def seed(
    environment: str = typer.Option("development", help="Environment to seed data for"),
    data_file: Path | None = typer.Option(None, help="Optional JSON file with custom seed data"),
) -> None:
    """Seed the database with test data."""

    async def _seed() -> None:
        logger.info(f"Starting database seeding for {environment} environment")
        if data_file:
            logger.debug(f"Using custom seed data from {data_file}")

        async with async_session() as session:
            await seed_data(session)
            logger.info(f"Successfully seeded {environment} database")

    asyncio.run(_seed())


if __name__ == "__main__":
    app()
