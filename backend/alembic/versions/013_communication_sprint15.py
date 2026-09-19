"""communication sprint15

Revision ID: 013
Revises: 012
Create Date: 2026-09-17

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tuteurs", sa.Column("user_id", sa.Uuid(), nullable=True))
    op.create_index("ix_tuteurs_user_id", "tuteurs", ["user_id"], unique=False)
    op.create_foreign_key("fk_tuteurs_user_id", "tuteurs", "users", ["user_id"], ["id"], ondelete="SET NULL")

    op.create_table(
        "annonces",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("titre", sa.String(length=200), nullable=False),
        sa.Column("contenu", sa.Text(), nullable=False),
        sa.Column("audience", sa.String(length=20), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("date_publication", sa.Date(), nullable=True),
        sa.Column("date_expiration", sa.Date(), nullable=True),
        sa.Column("auteur_id", sa.Uuid(), nullable=True),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["auteur_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "modeles_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("libelle", sa.String(length=100), nullable=False),
        sa.Column("sujet", sa.String(length=200), nullable=False),
        sa.Column("corps", sa.Text(), nullable=False),
        sa.Column("canal", sa.String(length=20), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "historique_communications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("modele_id", sa.Uuid(), nullable=True),
        sa.Column("annonce_id", sa.Uuid(), nullable=True),
        sa.Column("canal", sa.String(length=20), nullable=False),
        sa.Column("destinataire", sa.String(length=255), nullable=False),
        sa.Column("sujet", sa.String(length=200), nullable=False),
        sa.Column("corps", sa.Text(), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("envoye_par_id", sa.Uuid(), nullable=True),
        sa.Column("eleve_id", sa.Uuid(), nullable=True),
        sa.Column("envoye_le", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annonce_id"], ["annonces.id"]),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"]),
        sa.ForeignKeyConstraint(["envoye_par_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["modele_id"], ["modeles_messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("historique_communications")
    op.drop_table("modeles_messages")
    op.drop_table("annonces")
    op.drop_constraint("fk_tuteurs_user_id", "tuteurs", type_="foreignkey")
    op.drop_index("ix_tuteurs_user_id", table_name="tuteurs")
    op.drop_column("tuteurs", "user_id")
