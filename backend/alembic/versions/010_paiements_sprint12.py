"""paiements sprint12

Revision ID: 010
Revises: 009
Create Date: 2026-09-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tarifs_niveaux",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("niveau_id", sa.Uuid(), nullable=False),
        sa.Column("type_frais_id", sa.Uuid(), nullable=False),
        sa.Column("montant", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["niveau_id"], ["niveaux.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["type_frais_id"], ["types_frais.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("annee_scolaire_id", "niveau_id", "type_frais_id", name="uq_tarif_annee_niveau_type"),
    )

    op.create_table(
        "tranches_frais",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("type_frais_id", sa.Uuid(), nullable=False),
        sa.Column("libelle", sa.String(length=100), nullable=False),
        sa.Column("date_echeance", sa.Date(), nullable=False),
        sa.Column("ordre", sa.Integer(), nullable=False),
        sa.Column("pourcentage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["type_frais_id"], ["types_frais.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("annee_scolaire_id", "type_frais_id", "ordre", name="uq_tranche_annee_type_ordre"),
    )

    op.create_table(
        "remises_eleves",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("type_frais_id", sa.Uuid(), nullable=True),
        sa.Column("montant", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("pourcentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("motif", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["type_frais_id"], ["types_frais.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sequences_recu",
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("dernier_numero", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("annee_scolaire_id"),
    )

    op.create_table(
        "paiements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("type_frais_id", sa.Uuid(), nullable=False),
        sa.Column("tranche_id", sa.Uuid(), nullable=True),
        sa.Column("montant", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("remise_montant", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("mode_paiement", sa.String(length=20), nullable=False),
        sa.Column("reference_externe", sa.String(length=100), nullable=True),
        sa.Column("date_paiement", sa.Date(), nullable=False),
        sa.Column("numero_recu", sa.String(length=30), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("encaisse_par_id", sa.Uuid(), nullable=True),
        sa.Column("paiement_origine_id", sa.Uuid(), nullable=True),
        sa.Column("motif_annulation", sa.Text(), nullable=True),
        sa.Column("libelle", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["encaisse_par_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["paiement_origine_id"], ["paiements.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tranche_id"], ["tranches_frais.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["type_frais_id"], ["types_frais.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("numero_recu"),
    )
    op.create_index("ix_paiements_eleve_id", "paiements", ["eleve_id"])
    op.create_index("ix_paiements_date_paiement", "paiements", ["date_paiement"])

    op.create_table(
        "relances_impayes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("tranche_id", sa.Uuid(), nullable=True),
        sa.Column("date_relance", sa.Date(), nullable=False),
        sa.Column("canal", sa.String(length=30), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tranche_id"], ["tranches_frais.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("relances_impayes")
    op.drop_table("paiements")
    op.drop_table("sequences_recu")
    op.drop_table("remises_eleves")
    op.drop_table("tranches_frais")
    op.drop_table("tarifs_niveaux")
