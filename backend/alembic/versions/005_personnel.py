"""personnel sprint7

Revision ID: 005
Revises: 004
Create Date: 2026-09-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "personnel",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("matricule", sa.String(length=20), nullable=False),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("prenoms", sa.String(length=150), nullable=False),
        sa.Column("sexe", sa.String(length=1), nullable=False),
        sa.Column("date_naissance", sa.Date(), nullable=True),
        sa.Column("telephone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("adresse", sa.String(length=500), nullable=True),
        sa.Column("categorie", sa.String(length=20), nullable=False),
        sa.Column("fonction", sa.String(length=100), nullable=True),
        sa.Column("specialite", sa.String(length=150), nullable=True),
        sa.Column("date_embauche", sa.Date(), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("matricule"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_personnel_matricule", "personnel", ["matricule"])
    op.create_index("ix_personnel_nom", "personnel", ["nom"])
    op.create_index("ix_personnel_prenoms", "personnel", ["prenoms"])
    op.create_index("ix_personnel_categorie", "personnel", ["categorie"])

    op.create_table(
        "diplomes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("personnel_id", sa.Uuid(), nullable=False),
        sa.Column("libelle", sa.String(length=200), nullable=False),
        sa.Column("etablissement", sa.String(length=200), nullable=True),
        sa.Column("annee_obtention", sa.Integer(), nullable=True),
        sa.Column("niveau", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["personnel_id"], ["personnel.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "contrats",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("personnel_id", sa.Uuid(), nullable=False),
        sa.Column("type_contrat", sa.String(length=20), nullable=False),
        sa.Column("date_debut", sa.Date(), nullable=False),
        sa.Column("date_fin", sa.Date(), nullable=True),
        sa.Column("salaire_mensuel", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["personnel_id"], ["personnel.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "affectations_pedagogiques",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("personnel_id", sa.Uuid(), nullable=False),
        sa.Column("classe_id", sa.Uuid(), nullable=False),
        sa.Column("matiere_id", sa.Uuid(), nullable=False),
        sa.Column("annee_scolaire_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["annee_scolaire_id"], ["annees_scolaires.id"]),
        sa.ForeignKeyConstraint(["classe_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["matiere_id"], ["matieres.id"]),
        sa.ForeignKeyConstraint(["personnel_id"], ["personnel.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "personnel_id",
            "classe_id",
            "matiere_id",
            "annee_scolaire_id",
            name="uq_affectation_personnel_classe_matiere_annee",
        ),
    )

    op.create_table(
        "conges_absences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("personnel_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("date_debut", sa.Date(), nullable=False),
        sa.Column("date_fin", sa.Date(), nullable=False),
        sa.Column("motif", sa.Text(), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["personnel_id"], ["personnel.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("classes", sa.Column("titulaire_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_classes_titulaire_id",
        "classes",
        "personnel",
        ["titulaire_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_classes_titulaire_id", "classes", type_="foreignkey")
    op.drop_column("classes", "titulaire_id")
    op.drop_table("conges_absences")
    op.drop_table("affectations_pedagogiques")
    op.drop_table("contrats")
    op.drop_table("diplomes")
    op.drop_index("ix_personnel_categorie", "personnel")
    op.drop_index("ix_personnel_prenoms", "personnel")
    op.drop_index("ix_personnel_nom", "personnel")
    op.drop_index("ix_personnel_matricule", "personnel")
    op.drop_table("personnel")
