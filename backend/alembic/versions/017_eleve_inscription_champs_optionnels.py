"""Champs élève / tuteur optionnels à l'inscription

Revision ID: 017
Revises: 016
Create Date: 2026-10-07

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("eleves", "nom", existing_type=sa.String(length=100), nullable=True)
    op.alter_column("eleves", "prenoms", existing_type=sa.String(length=150), nullable=True)
    op.alter_column("eleves", "sexe", existing_type=sa.String(length=1), nullable=True)
    op.alter_column("eleves", "date_naissance", existing_type=sa.Date(), nullable=True)
    op.alter_column("tuteurs", "nom", existing_type=sa.String(length=100), nullable=True)
    op.alter_column("tuteurs", "prenoms", existing_type=sa.String(length=150), nullable=True)
    op.alter_column("tuteurs", "telephone", existing_type=sa.String(length=20), nullable=True)


def downgrade() -> None:
    op.alter_column("tuteurs", "telephone", existing_type=sa.String(length=20), nullable=False)
    op.alter_column("tuteurs", "prenoms", existing_type=sa.String(length=150), nullable=False)
    op.alter_column("tuteurs", "nom", existing_type=sa.String(length=100), nullable=False)
    op.alter_column("eleves", "date_naissance", existing_type=sa.Date(), nullable=False)
    op.alter_column("eleves", "sexe", existing_type=sa.String(length=1), nullable=False)
    op.alter_column("eleves", "prenoms", existing_type=sa.String(length=150), nullable=False)
    op.alter_column("eleves", "nom", existing_type=sa.String(length=100), nullable=False)
