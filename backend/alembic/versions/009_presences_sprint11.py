"""presences sprint11

Revision ID: 009
Revises: 008
Create Date: 2026-09-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "appels_presence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("classe_id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("saisi_par_id", sa.Uuid(), nullable=True),
        sa.Column("remarque", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["classe_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["saisi_par_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("classe_id", "date", name="uq_appel_classe_date"),
    )
    op.create_index("ix_appels_presence_classe_id", "appels_presence", ["classe_id"])
    op.create_index("ix_appels_presence_date", "appels_presence", ["date"])

    op.create_table(
        "presences_eleves",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("appel_id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("retard_minutes", sa.Integer(), nullable=True),
        sa.Column("motif", sa.Text(), nullable=True),
        sa.Column("justification", sa.Text(), nullable=True),
        sa.Column("justification_statut", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["appel_id"], ["appels_presence.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("appel_id", "eleve_id", name="uq_presence_appel_eleve"),
    )
    op.create_index("ix_presences_eleves_appel_id", "presences_eleves", ["appel_id"])
    op.create_index("ix_presences_eleves_eleve_id", "presences_eleves", ["eleve_id"])

    op.create_table(
        "incidents_disciplinaires",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("eleve_id", sa.Uuid(), nullable=False),
        sa.Column("classe_id", sa.Uuid(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("sanction", sa.Text(), nullable=True),
        sa.Column("saisi_par_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["classe_id"], ["classes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["eleve_id"], ["eleves.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["saisi_par_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_incidents_disciplinaires_eleve_id", "incidents_disciplinaires", ["eleve_id"])
    op.create_index("ix_incidents_disciplinaires_classe_id", "incidents_disciplinaires", ["classe_id"])
    op.create_index("ix_incidents_disciplinaires_date", "incidents_disciplinaires", ["date"])


def downgrade() -> None:
    op.drop_table("incidents_disciplinaires")
    op.drop_table("presences_eleves")
    op.drop_table("appels_presence")
