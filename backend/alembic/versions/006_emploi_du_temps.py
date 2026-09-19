"""emploi du temps sprint8

Revision ID: 006
Revises: 005
Create Date: 2026-09-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "creneaux_horaires",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("libelle", sa.String(length=50), nullable=False),
        sa.Column("heure_debut", sa.Time(), nullable=False),
        sa.Column("heure_fin", sa.Time(), nullable=False),
        sa.Column("ordre", sa.Integer(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("annee_scolaire_id", "ordre", name="uq_creneau_annee_ordre"),
    )

    op.create_table(
        "seances_cours",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("classe_id", sa.Uuid(), nullable=False),
        sa.Column("creneau_id", sa.Uuid(), nullable=False),
        sa.Column("jour_semaine", sa.Integer(), nullable=False),
        sa.Column("matiere_id", sa.Uuid(), nullable=False),
        sa.Column("personnel_id", sa.Uuid(), nullable=False),
        sa.Column("salle", sa.String(length=100), nullable=True),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["classe_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["creneau_id"], ["creneaux_horaires.id"]),
        sa.ForeignKeyConstraint(["matiere_id"], ["matieres.id"]),
        sa.ForeignKeyConstraint(["personnel_id"], ["personnel.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "classe_id",
            "creneau_id",
            "jour_semaine",
            "annee_scolaire_id",
            name="uq_seance_classe_creneau_jour",
        ),
    )


def downgrade() -> None:
    op.drop_table("seances_cours")
    op.drop_table("creneaux_horaires")
