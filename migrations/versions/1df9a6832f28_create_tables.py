"""create_tables

Revision ID: 1df9a6832f28
Revises:
Create Date: 2024-03-19 01:46:15.123456

"""

from collections.abc import Sequence
from datetime import datetime
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1df9a6832f28"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create universes table
    universes = op.create_table(
        "universes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("currency_type", sa.String(), nullable=False),
        sa.Column("exchange_rate", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create users table
    users = op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("universe_id", sa.Integer(), nullable=False),
        sa.Column("balance", sa.Float(), nullable=False, default=1000.0),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["universe_id"], ["universes.id"]),
    )

    # Create items table
    items = op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("universe_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["universe_id"], ["universes.id"]),
    )

    # Create transactions table
    transactions = op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("buyer_id", sa.Integer(), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("from_universe_id", sa.Integer(), nullable=False),
        sa.Column("to_universe_id", sa.Integer(), nullable=False),
        sa.Column("transaction_time", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["buyer_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"]),
        sa.ForeignKeyConstraint(["from_universe_id"], ["universes.id"]),
        sa.ForeignKeyConstraint(["to_universe_id"], ["universes.id"]),
    )


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("items")
    op.drop_table("users")
    op.drop_table("universes")
