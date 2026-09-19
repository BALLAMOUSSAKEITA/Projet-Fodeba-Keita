"""eleves tables

Revision ID: 003
Revises: 002
Create Date: 2026-09-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "eleves",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("matricule", sa.String(length=20), nullable=False),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("prenoms", sa.String(length=150), nullable=False),
        sa.Column("sexe", sa.String(length=1), nullable=False),
        sa.Column("date_naissance", sa.Date(), nullable=False),
        sa.Column("lieu_naissance", sa.String(length=150), nullable=True),
        sa.Column("nationalite", sa.String(length=50), nullable=True),
        sa.Column("adresse", sa.String(length=500), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("groupe_sanguin", sa.String(length=10), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("matricule"),
    )
    op.create_index(op.f("ix_eleves_matricule"), "eleves", ["matricule"], unique=True)
    op.create_index(op.f("ix_eleves_nom"), "eleves", ["nom"], unique=False)
    op.create_index(op.f("ix_eleves_prenoms"), "eleves", ["prenoms"], unique=False)

    op.create_table(
        "tuteurs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("prenoms", sa.String(length=150), nullable=False),
        sa.Column("telephone", sa.String(length=20), nullable=False),
        sa.Column("profession", sa.String(length=100), nullable=True),
        sa.Column("adresse", sa.String(length=500), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "inscriptions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("niveau_id", sa.Uuid(), nullable=False),
        sa.Column("classe_id", sa.Uuid(), nullable=True),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("date_inscription", sa.Date(), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["classe_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["niveau_id"], ["niveaux.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("eleve_id", "annee_scolaire_id", name="uq_inscription_eleve_annee"),
    )


def downgrade() -> None:
    op.drop_table("inscriptions")
    op.drop_table("tuteurs")
    op.drop_index(op.f("ix_eleves_prenoms"), table_name="eleves")
    op.drop_index(op.f("ix_eleves_nom"), table_name="eleves")
    op.drop_index(op.f("ix_eleves_matricule"), table_name="eleves")
    op.drop_table("eleves")
