from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comptabilite import (
    BudgetLigne,
    CategorieDepense,
    CompteTresorerie,
    TypeCompteTresorerie,
)
from app.models.parametrage import AnneeScolaire

CATEGORIES = [
    ("SALAIRES", "Salaires & charges sociales"),
    ("FOURNITURES", "Fournitures scolaires"),
    ("ENTRETIEN", "Entretien & maintenance"),
    ("EAU_ELEC", "Eau & électricité"),
    ("TRANSPORT", "Transport scolaire"),
    ("COMMUNICATION", "Communication & marketing"),
    ("DIVERS", "Dépenses diverses"),
]

BUDGET_2025 = {
    "SALAIRES": Decimal("45000000"),
    "FOURNITURES": Decimal("8000000"),
    "ENTRETIEN": Decimal("5000000"),
    "EAU_ELEC": Decimal("6000000"),
    "TRANSPORT": Decimal("4000000"),
    "COMMUNICATION": Decimal("2000000"),
    "DIVERS": Decimal("3000000"),
}


async def seed_comptabilite(db: AsyncSession) -> None:
    existing = await db.execute(select(CategorieDepense).limit(1))
    if existing.scalar_one_or_none() is not None:
        return

    cats: dict[str, CategorieDepense] = {}
    for code, libelle in CATEGORIES:
        cat = CategorieDepense(code=code, libelle=libelle, actif=True)
        db.add(cat)
        cats[code] = cat
    await db.flush()

    db.add(CompteTresorerie(
        code="CAISSE",
        libelle="Caisse principale",
        type=TypeCompteTresorerie.CAISSE.value,
        solde_initial=Decimal("5000000"),
        actif=True,
    ))
    db.add(CompteTresorerie(
        code="BANQUE",
        libelle="Compte bancaire UBA",
        type=TypeCompteTresorerie.BANQUE.value,
        solde_initial=Decimal("25000000"),
        actif=True,
    ))

    annee_result = await db.execute(
        select(AnneeScolaire).where(AnneeScolaire.is_active.is_(True)).limit(1)
    )
    annee = annee_result.scalar_one_or_none()
    if annee:
        for code, montant in BUDGET_2025.items():
            db.add(
                BudgetLigne(
                    annee_scolaire_id=annee.id,
                    categorie_id=cats[code].id,
                    montant_prevu=montant,
                )
            )

    await db.flush()
