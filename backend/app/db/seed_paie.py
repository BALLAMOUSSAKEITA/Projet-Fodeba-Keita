from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personnel import Contrat, Personnel, TypeContrat
from app.models.paie import PeriodePaie


async def seed_paie(db: AsyncSession) -> None:
    existing = await db.execute(select(PeriodePaie).limit(1))
    if existing.scalar_one_or_none() is not None:
        return

    db.add(PeriodePaie(annee=2025, mois=9, libelle="Septembre 2025"))

    for matricule, salaire in [("PER-0001", Decimal("2800000")), ("PER-0002", Decimal("1800000"))]:
        result = await db.execute(select(Personnel).where(Personnel.matricule == matricule))
        pers = result.scalar_one_or_none()
        if pers is None:
            continue
        contrat_exists = await db.execute(
            select(Contrat.id).where(Contrat.personnel_id == pers.id).limit(1)
        )
        if contrat_exists.scalar_one_or_none() is not None:
            continue
        db.add(
            Contrat(
                personnel_id=pers.id,
                type_contrat=TypeContrat.CDI.value,
                date_debut=date(2021, 1, 1),
                salaire_mensuel=salaire,
                statut="actif",
            )
        )

    await db.flush()
