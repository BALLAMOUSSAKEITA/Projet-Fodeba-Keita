from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parametrage import AnneeScolaire, Niveau, TypeFrais
from app.models.paiements import SequenceRecu, TarifNiveau, TrancheFrais

# Montants de base scolarité par ordre de niveau (GNF)
SCOLARITE_PAR_ORDRE = {
    1: Decimal("1500000"),   # PS
    2: Decimal("1500000"),   # MS
    3: Decimal("1800000"),   # GS
    4: Decimal("2000000"),   # 1A
    5: Decimal("2200000"),   # 2A
    6: Decimal("2400000"),   # 3A
    7: Decimal("2600000"),   # 4A
    8: Decimal("2800000"),   # 5A
    9: Decimal("3000000"),   # 6A
}

INSCRIPTION = Decimal("300000")
CANTINE = Decimal("400000")
TRANSPORT = Decimal("600000")


async def seed_paiements(db: AsyncSession) -> None:
    annee_result = await db.execute(
        select(AnneeScolaire).where(AnneeScolaire.is_active.is_(True)).limit(1)
    )
    annee = annee_result.scalar_one_or_none()
    if annee is None:
        return

    existing = await db.execute(
        select(TarifNiveau.id).where(TarifNiveau.annee_scolaire_id == annee.id).limit(1)
    )
    if existing.scalar_one_or_none() is not None:
        return

    niveaux = list((await db.execute(select(Niveau).order_by(Niveau.ordre))).scalars().all())
    types_frais = {
        tf.code: tf
        for tf in (await db.execute(select(TypeFrais).where(TypeFrais.actif.is_(True)))).scalars().all()
    }

    for niveau in niveaux:
        scolarite = SCOLARITE_PAR_ORDRE.get(niveau.ordre, Decimal("2000000"))
        if "INSCRIPTION" in types_frais:
            db.add(
                TarifNiveau(
                    annee_scolaire_id=annee.id,
                    niveau_id=niveau.id,
                    type_frais_id=types_frais["INSCRIPTION"].id,
                    montant=INSCRIPTION,
                )
            )
        if "SCOLARITE" in types_frais:
            db.add(
                TarifNiveau(
                    annee_scolaire_id=annee.id,
                    niveau_id=niveau.id,
                    type_frais_id=types_frais["SCOLARITE"].id,
                    montant=scolarite,
                )
            )
        if "CANTINE" in types_frais:
            db.add(
                TarifNiveau(
                    annee_scolaire_id=annee.id,
                    niveau_id=niveau.id,
                    type_frais_id=types_frais["CANTINE"].id,
                    montant=CANTINE,
                )
            )
        if "TRANSPORT" in types_frais:
            db.add(
                TarifNiveau(
                    annee_scolaire_id=annee.id,
                    niveau_id=niveau.id,
                    type_frais_id=types_frais["TRANSPORT"].id,
                    montant=TRANSPORT,
                )
            )

    if "SCOLARITE" in types_frais:
        scol_id = types_frais["SCOLARITE"].id
        tranches = [
            ("1ère tranche — Inscription", "2025-10-15", 1, Decimal("40")),
            ("2ème tranche — Trimestre 2", "2026-01-15", 2, Decimal("30")),
            ("3ème tranche — Trimestre 3", "2026-04-15", 3, Decimal("30")),
        ]
        from datetime import date as dt

        for libelle, echeance, ordre, pct in tranches:
            db.add(
                TrancheFrais(
                    annee_scolaire_id=annee.id,
                    type_frais_id=scol_id,
                    libelle=libelle,
                    date_echeance=dt.fromisoformat(echeance),
                    ordre=ordre,
                    pourcentage=pct,
                )
            )

    db.add(SequenceRecu(annee_scolaire_id=annee.id, dernier_numero=0))
    await db.flush()
