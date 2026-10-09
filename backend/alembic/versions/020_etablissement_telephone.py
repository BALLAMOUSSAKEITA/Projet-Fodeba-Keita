"""Téléphone officiel établissement 626137290

Revision ID: 020
Revises: 019
Create Date: 2026-10-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "020"
down_revision: Union[str, None] = "019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TELEPHONE = "+224626137290"


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE etablissements SET telephone = :tel"), {"tel": TELEPHONE})


def downgrade() -> None:
    pass
