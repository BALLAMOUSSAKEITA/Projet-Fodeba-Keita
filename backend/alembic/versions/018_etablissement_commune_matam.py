"""Commune de l'établissement : Matam (au lieu de Ratoma)

Revision ID: 018
Revises: 017
Create Date: 2026-10-07

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

ADRESSE = "Commune de Matam, Conakry"
COMMUNE = "Matam"

revision: str = "018"
down_revision: Union[str, None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE etablissements
            SET commune = :commune,
                adresse = :adresse
            WHERE commune ILIKE 'Ratoma'
               OR adresse ILIKE '%Ratoma%'
            """
        ),
        {"commune": COMMUNE, "adresse": ADRESSE},
    )
    conn.execute(
        sa.text(
            """
            UPDATE etablissements
            SET commune = COALESCE(commune, :commune),
                adresse = COALESCE(adresse, :adresse)
            WHERE commune IS NULL OR adresse IS NULL
            """
        ),
        {"commune": COMMUNE, "adresse": ADRESSE},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE etablissements
            SET commune = 'Ratoma',
                adresse = 'Commune de Ratoma, Conakry'
            WHERE commune ILIKE 'Matam'
               OR adresse ILIKE '%Matam%'
            """
        )
    )
