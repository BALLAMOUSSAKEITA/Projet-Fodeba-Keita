"""comptabilite sprint14

Revision ID: 012
Revises: 011
Create Date: 2026-09-17

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories_depenses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("libelle", sa.String(length=100), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "comptes_tresorerie",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("libelle", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("solde_initial", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "budget_lignes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("categorie_id", sa.Uuid(), nullable=False),
        sa.Column("montant_prevu", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["categorie_id"], ["categories_depenses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("annee_scolaire_id", "categorie_id", name="uq_budget_annee_categorie"),
    )

    op.create_table(
        "depenses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("categorie_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("libelle", sa.String(length=255), nullable=False),
        sa.Column("montant", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("date_depense", sa.Date(), nullable=False),
        sa.Column("compte_tresorerie_id", sa.Uuid(), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("saisi_par_id", sa.Uuid(), nullable=True),
        sa.Column("valide_par_id", sa.Uuid(), nullable=True),
        sa.Column("motif_refus", sa.Text(), nullable=True),
        sa.Column("reference_piece", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["categorie_id"], ["categories_depenses.id"]),
        sa.ForeignKeyConstraint(["compte_tresorerie_id"], ["comptes_tresorerie.id"]),
        sa.ForeignKeyConstraint(["saisi_par_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["valide_par_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_depenses_categorie_id", "depenses", ["categorie_id"])
    op.create_index("ix_depenses_date_depense", "depenses", ["date_depense"])

    op.create_table(
        "ecritures_comptables",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("date_ecriture", sa.Date(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("libelle", sa.String(length=255), nullable=False),
        sa.Column("montant", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("compte_tresorerie_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=True),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["compte_tresorerie_id"], ["comptes_tresorerie.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ecritures_comptables_date", "ecritures_comptables", ["date_ecriture"])


def downgrade() -> None:
    op.drop_table("ecritures_comptables")
    op.drop_table("depenses")
    op.drop_table("budget_lignes")
    op.drop_table("comptes_tresorerie")
    op.drop_table("categories_depenses")
