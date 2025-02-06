"""Command line interface for multiverse market."""
import asyncio
import typer
from typing import Optional
from pathlib import Path

from .scripts.seed_data import seed_data
from .dependencies import async_session

app = typer.Typer()

@app.command()
def seed(
    environment: str = typer.Option("development", help="Environment to seed data for"),
    data_file: Optional[Path] = typer.Option(None, help="Optional JSON file with custom seed data")
) -> None:
    """Seed the database with test data."""
    async def _seed() -> None:
        async with async_session() as session:
            await seed_data(session)
            typer.echo(f"Successfully seeded {environment} database")

    asyncio.run(_seed())

if __name__ == "__main__":
    app() 