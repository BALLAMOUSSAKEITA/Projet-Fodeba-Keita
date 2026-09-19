"""parametrage tables

Revision ID: 002
Revises: 001
Create Date: 2026-09-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "etablissements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nom", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("adresse", sa.String(length=500), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("prefecture", sa.String(length=100), nullable=True),
        sa.Column("commune", sa.String(length=100), nullable=True),
        sa.Column("telephone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("devise_principale", sa.String(length=10), nullable=False),
        sa.Column("devise_secondaire", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "annees_scolaires",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("libelle", sa.String(length=20), nullable=False),
        sa.Column("date_debut", sa.Date(), nullable=False),
        sa.Column("date_fin", sa.Date(), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("libelle"),
    )
    op.create_table(
        "niveaux",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("libelle", sa.String(length=100), nullable=False),
        sa.Column("ordre", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "matieres",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("libelle", sa.String(length=100), nullable=False),
        sa.Column("coefficient_defaut", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "types_frais",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("libelle", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "referentiels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("libelle", sa.String(length=150), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["referentiels.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("type", "code", name="uq_referentiel_type_code"),
    )
    op.create_index(op.f("ix_referentiels_type"), "referentiels", ["type"], unique=False)
    op.create_table(
        "matiere_niveaux",
        sa.Column("matiere_id", sa.Uuid(), nullable=False),
        sa.Column("niveau_id", sa.Uuid(), nullable=False),
        sa.Column("coefficient", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["matiere_id"], ["matieres.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["niveau_id"], ["niveaux.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("matiere_id", "niveau_id"),
    )
    op.create_table(
        "classes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nom", sa.String(length=50), nullable=False),
        sa.Column("capacite_max", sa.Integer(), nullable=False),
        sa.Column("salle", sa.String(length=100), nullable=True),
        sa.Column("niveau_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["niveau_id"], ["niveaux.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("annee_scolaire_id", "niveau_id", "nom", name="uq_classe_annee_niveau_nom"),
    )
    op.create_table(
        "periodes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("libelle", sa.String(length=50), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("date_debut", sa.Date(), nullable=False),
        sa.Column("date_fin", sa.Date(), nullable=False),
        sa.Column("ordre", sa.Integer(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("annee_scolaire_id", "ordre", name="uq_periode_annee_ordre"),
    )
    op.create_table(
        "baremes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("echelle", sa.String(length=10), nullable=False),
        sa.Column("arrondi_decimales", sa.Integer(), nullable=False),
        sa.Column("seuil_passage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("seuil_redoublement", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("annee_scolaire_id"),
    )
    op.create_table(
        "calendrier_scolaire",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("libelle", sa.String(length=150), nullable=False),
        sa.Column("date_debut", sa.Date(), nullable=False),
        sa.Column("date_fin", sa.Date(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("calendrier_scolaire")
    op.drop_table("baremes")
    op.drop_table("periodes")
    op.drop_table("classes")
    op.drop_table("matiere_niveaux")
    op.drop_index(op.f("ix_referentiels_type"), table_name="referentiels")
    op.drop_table("referentiels")
    op.drop_table("types_frais")
    op.drop_table("matieres")
    op.drop_table("niveaux")
    op.drop_table("annees_scolaires")
    op.drop_table("etablissements")
