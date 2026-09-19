"""eleves sprint6 fields

Revision ID: 004
Revises: 003
Create Date: 2026-09-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("eleves", sa.Column("motif_inactivite", sa.String(length=255), nullable=True))
    op.add_column("eleves", sa.Column("date_inactivite", sa.Date(), nullable=True))

    op.create_table(
        "transferts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("ecole", sa.String(length=255), nullable=False),
        sa.Column("date_transfert", sa.Date(), nullable=False),
        sa.Column("motif", sa.Text(), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("transferts")
    op.drop_column("eleves", "date_inactivite")
    op.drop_column("eleves", "motif_inactivite")
