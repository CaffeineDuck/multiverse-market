"""add_timezone_to_transaction_time

Revision ID: 51bddb579501
Revises: 1df9a6832f28
Create Date: 2025-02-08 18:28:37.761516

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "51bddb579501"
down_revision: str = "1df9a6832f28"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Modify transaction_time column to use TIMESTAMP WITH TIME ZONE
    op.alter_column(
        "transactions",
        "transaction_time",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="transaction_time AT TIME ZONE 'UTC'"
    )


def downgrade() -> None:
    # Convert back to TIMESTAMP WITHOUT TIME ZONE
    op.alter_column(
        "transactions",
        "transaction_time",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="transaction_time AT TIME ZONE 'UTC'"
    )
