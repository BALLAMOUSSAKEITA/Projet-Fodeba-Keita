"""Purge année 2025-2026 et activation 2026-2027

Revision ID: 016
Revises: 015
Create Date: 2026-10-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LIBELLE_PURGE = "2025-2026"
LIBELLE_ACTIVE = "2026-2027"


def _table_exists(conn, name: str) -> bool:
    row = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = :name"
        ),
        {"name": name},
    ).first()
    return row is not None


def upgrade() -> None:
    conn = op.get_bind()
    annee_row = conn.execute(
        sa.text("SELECT id FROM annees_scolaires WHERE libelle = :libelle"),
        {"libelle": LIBELLE_PURGE},
    ).first()
    if annee_row is None:
        _ensure_active_year(conn)
        return

    aid = str(annee_row[0])

    if _table_exists(conn, "historique_paiements"):
        conn.execute(
            sa.text(
                """
                DELETE FROM historique_paiements
                WHERE annee_scolaire_id = :aid
                   OR paiement_id IN (SELECT id FROM paiements WHERE annee_scolaire_id = :aid)
                """
            ),
            {"aid": aid},
        )

    conn.execute(
        sa.text("UPDATE paiements SET paiement_origine_id = NULL WHERE annee_scolaire_id = :aid"),
        {"aid": aid},
    )
    for table in (
        "paiements",
        "relances_impayes",
        "remises_eleves",
        "sequences_recu",
        "tarifs_niveaux",
        "tranches_frais",
        "seances_cours",
        "creneaux_horaires",
        "affectations_pedagogiques",
        "inscriptions",
        "depenses",
        "budget_lignes",
        "calendrier_scolaire",
        "periodes",
        "classes",
        "baremes",
    ):
        if _table_exists(conn, table):
            conn.execute(
                sa.text(f"DELETE FROM {table} WHERE annee_scolaire_id = :aid"),
                {"aid": aid},
            )

    if _table_exists(conn, "ecritures_comptables"):
        conn.execute(
            sa.text("DELETE FROM ecritures_comptables WHERE annee_scolaire_id = :aid"),
            {"aid": aid},
        )

    if _table_exists(conn, "eleves"):
        conn.execute(
            sa.text(
                """
                DELETE FROM eleves e
                WHERE NOT EXISTS (SELECT 1 FROM inscriptions i WHERE i.eleve_id = e.id)
                """
            )
        )

    conn.execute(
        sa.text("DELETE FROM annees_scolaires WHERE id = :aid"),
        {"aid": aid},
    )

    _ensure_active_year(conn)


def _ensure_active_year(conn) -> None:
    conn.execute(sa.text("UPDATE annees_scolaires SET is_active = false"))
    row = conn.execute(
        sa.text("SELECT id FROM annees_scolaires WHERE libelle = :libelle"),
        {"libelle": LIBELLE_ACTIVE},
    ).first()
    if row is None:
        conn.execute(
            sa.text(
                """
                INSERT INTO annees_scolaires (id, libelle, date_debut, date_fin, statut, is_active, created_at, updated_at)
                VALUES (
                    gen_random_uuid(),
                    :libelle,
                    DATE '2026-09-15',
                    DATE '2027-07-15',
                    'active',
                    true,
                    now(),
                    now()
                )
                """
            ),
            {"libelle": LIBELLE_ACTIVE},
        )
        row = conn.execute(
            sa.text("SELECT id FROM annees_scolaires WHERE libelle = :libelle"),
            {"libelle": LIBELLE_ACTIVE},
        ).first()
    else:
        conn.execute(
            sa.text(
                """
                UPDATE annees_scolaires
                SET is_active = true, statut = 'active'
                WHERE libelle = :libelle
                """
            ),
            {"libelle": LIBELLE_ACTIVE},
        )

    if row and _table_exists(conn, "baremes"):
        bid = str(row[0])
        exists_bareme = conn.execute(
            sa.text("SELECT 1 FROM baremes WHERE annee_scolaire_id = :aid"),
            {"aid": bid},
        ).first()
        if not exists_bareme:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO baremes (id, annee_scolaire_id, echelle, arrondi_decimales, seuil_passage, seuil_redoublement, created_at, updated_at)
                    VALUES (gen_random_uuid(), :aid, '/20', 2, 10, 8, now(), now())
                    """
                ),
                {"aid": bid},
            )


def downgrade() -> None:
    raise NotImplementedError("Restauration de l'année 2025-2026 non supportée")
