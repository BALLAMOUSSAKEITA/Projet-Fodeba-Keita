"""paie sprint13

Revision ID: 011
Revises: 010
Create Date: 2026-09-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "periodes_paie",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("annee", sa.Integer(), nullable=False),
        sa.Column("mois", sa.Integer(), nullable=False),
        sa.Column("libelle", sa.String(length=50), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("annee", "mois", name="uq_periode_paie_annee_mois"),
    )

    op.create_table(
        "bulletins_paie",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("personnel_id", sa.Uuid(), nullable=False),
        sa.Column("periode_paie_id", sa.Uuid(), nullable=False),
        sa.Column("salaire_base", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("prime_anciennete", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("prime_autre", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("indemnite_transport", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("indemnite_logement", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("retenue_cnss", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("retenue_its", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("retenue_absences", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("retenue_avances", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("autres_retenues", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("brut", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("net_a_payer", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("jours_absence", sa.Integer(), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("paye_par_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["paye_par_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["periode_paie_id"], ["periodes_paie.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["personnel_id"], ["personnel.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("personnel_id", "periode_paie_id", name="uq_bulletin_personnel_periode"),
    )
    op.create_index("ix_bulletins_paie_personnel_id", "bulletins_paie", ["personnel_id"])
    op.create_index("ix_bulletins_paie_periode_paie_id", "bulletins_paie", ["periode_paie_id"])

    op.create_table(
        "avances_salaire",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("personnel_id", sa.Uuid(), nullable=False),
        sa.Column("montant", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("date_avance", sa.Date(), nullable=False),
        sa.Column("motif", sa.Text(), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("bulletin_paie_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["bulletin_paie_id"], ["bulletins_paie.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["personnel_id"], ["personnel.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_avances_salaire_personnel_id", "avances_salaire", ["personnel_id"])


def downgrade() -> None:
    op.drop_table("avances_salaire")
    op.drop_table("bulletins_paie")
    op.drop_table("periodes_paie")
