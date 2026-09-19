"""notes sprint9

Revision ID: 007
Revises: 006
Create Date: 2026-09-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "types_evaluation",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("libelle", sa.String(length=100), nullable=False),
        sa.Column("coefficient_defaut", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("annee_scolaire_id", "code", name="uq_type_eval_annee_code"),
    )

    op.create_table(
        "evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("libelle", sa.String(length=100), nullable=False),
        sa.Column("classe_id", sa.Uuid(), nullable=False),
        sa.Column("matiere_id", sa.Uuid(), nullable=False),
        sa.Column("periode_id", sa.Uuid(), nullable=False),
        sa.Column("type_evaluation_id", sa.Uuid(), nullable=False),
        sa.Column("coefficient", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("date_evaluation", sa.Date(), nullable=True),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["classe_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["matiere_id"], ["matieres.id"]),
        sa.ForeignKeyConstraint(["periode_id"], ["periodes.id"]),
        sa.ForeignKeyConstraint(["type_evaluation_id"], ["types_evaluation.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "notes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("evaluation_id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("valeur", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("is_absent", sa.Boolean(), nullable=False),
        sa.Column("appreciation_libre", sa.Text(), nullable=True),
        sa.Column("appreciation_auto", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"]),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evaluation_id", "eleve_id", name="uq_note_evaluation_eleve"),
    )

    op.create_table(
        "validations_periode",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("classe_id", sa.Uuid(), nullable=False),
        sa.Column("periode_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("verrouille", sa.Boolean(), nullable=False),
        sa.Column("valide_par_id", sa.Uuid(), nullable=True),
        sa.Column("date_validation", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["classe_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["periode_id"], ["periodes.id"]),
        sa.ForeignKeyConstraint(["valide_par_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("classe_id", "periode_id", name="uq_validation_classe_periode"),
    )


def downgrade() -> None:
    op.drop_table("validations_periode")
    op.drop_table("notes")
    op.drop_table("evaluations")
    op.drop_table("types_evaluation")
