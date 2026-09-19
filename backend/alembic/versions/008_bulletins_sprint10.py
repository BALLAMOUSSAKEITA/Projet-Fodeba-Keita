"""bulletins sprint10

Revision ID: 008
Revises: 007
Create Date: 2026-09-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "competences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("domaine", sa.String(length=100), nullable=False),
        sa.Column("libelle", sa.String(length=255), nullable=False),
        sa.Column("niveau_id", sa.Uuid(), nullable=False),
        sa.Column("ordre", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["niveau_id"], ["niveaux.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("niveau_id", "code", name="uq_competence_niveau_code"),
    )

    op.create_table(
        "evaluations_competences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("competence_id", sa.Uuid(), nullable=False),
        sa.Column("periode_id", sa.Uuid(), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("appreciation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["competence_id"], ["competences.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"]),
        sa.ForeignKeyConstraint(["periode_id"], ["periodes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("eleve_id", "competence_id", "periode_id", name="uq_eval_comp_eleve_periode"),
    )

    op.create_table(
        "decisions_passage",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=False),
        sa.Column("observation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("eleve_id", "annee_scolaire_id", name="uq_decision_eleve_annee"),
    )


def downgrade() -> None:
    op.drop_table("decisions_passage")
    op.drop_table("evaluations_competences")
    op.drop_table("competences")
