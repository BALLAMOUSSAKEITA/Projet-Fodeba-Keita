"""Retrait modules notes, bulletins, presences, communication

Revision ID: 015
Revises: 014
Create Date: 2026-10-05

"""

from typing import Sequence, Union

from alembic import op

revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("historique_communications")
    op.drop_table("annonces")
    op.drop_table("modeles_messages")

    op.drop_index("ix_incidents_disciplinaires_date", table_name="incidents_disciplinaires")
    op.drop_index("ix_incidents_disciplinaires_classe_id", table_name="incidents_disciplinaires")
    op.drop_index("ix_incidents_disciplinaires_eleve_id", table_name="incidents_disciplinaires")
    op.drop_table("incidents_disciplinaires")

    op.drop_index("ix_presences_eleves_eleve_id", table_name="presences_eleves")
    op.drop_index("ix_presences_eleves_appel_id", table_name="presences_eleves")
    op.drop_table("presences_eleves")

    op.drop_index("ix_appels_presence_date", table_name="appels_presence")
    op.drop_index("ix_appels_presence_classe_id", table_name="appels_presence")
    op.drop_table("appels_presence")

    op.drop_index("ix_historique_notes_eleve_id", table_name="historique_notes")
    op.drop_index("ix_historique_notes_evaluation_id", table_name="historique_notes")
    op.drop_table("historique_notes")

    op.drop_table("notes")
    op.drop_table("validations_periode")
    op.drop_table("evaluations")
    op.drop_table("types_evaluation")

    op.drop_table("evaluations_competences")
    op.drop_table("decisions_passage")
    op.drop_table("competences")


def downgrade() -> None:
    raise NotImplementedError("Restauration non supportée pour la migration 015")
