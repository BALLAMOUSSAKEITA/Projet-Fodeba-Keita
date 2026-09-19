"""securite sprint17

Revision ID: 014
Revises: 013
Create Date: 2026-09-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("user_email", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"])

    op.create_table(
        "historique_notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("note_id", sa.Uuid(), nullable=True),
        sa.Column("evaluation_id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("ancienne_valeur", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("nouvelle_valeur", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("ancien_absent", sa.Boolean(), nullable=True),
        sa.Column("nouveau_absent", sa.Boolean(), nullable=True),
        sa.Column("modifie_par_id", sa.Uuid(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"]),
        sa.ForeignKeyConstraint(["modifie_par_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_historique_notes_evaluation_id", "historique_notes", ["evaluation_id"])
    op.create_index("ix_historique_notes_eleve_id", "historique_notes", ["eleve_id"])

    op.create_table(
        "historique_paiements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("paiement_id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("montant", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("statut_avant", sa.String(length=20), nullable=True),
        sa.Column("statut_apres", sa.String(length=20), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("modifie_par_id", sa.Uuid(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"]),
        sa.ForeignKeyConstraint(["modifie_par_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["paiement_id"], ["paiements.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_historique_paiements_paiement_id", "historique_paiements", ["paiement_id"])
    op.create_index("ix_historique_paiements_eleve_id", "historique_paiements", ["eleve_id"])
