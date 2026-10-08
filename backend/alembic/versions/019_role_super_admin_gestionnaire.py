"""Libellé rôle super_admin → Gestionnaire

Revision ID: 019
Revises: 018
Create Date: 2026-10-07

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "019"
down_revision: Union[str, None] = "018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE roles
            SET label = 'Gestionnaire'
            WHERE code = 'super_admin'
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE roles
            SET label = 'Super administrateur'
            WHERE code = 'super_admin'
            """
        )
    )
