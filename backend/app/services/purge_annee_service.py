"""Suppression d'une année scolaire et de toutes les données qui y sont rattachées."""

from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import HistoriquePaiement
from app.models.comptabilite import BudgetLigne, Depense, EcritureComptable
from app.models.eleve import Eleve, Inscription
from app.models.emploi_du_temps import CreneauHoraire, SeanceCours
from app.models.parametrage import (
    AnneeScolaire,
    Bareme,
    CalendrierScolaire,
    Classe,
    Periode,
    StatutAnneeScolaire,
)
from app.models.paiements import Paiement, RelanceImpaye, RemiseEleve, SequenceRecu, TarifNiveau, TrancheFrais
from app.models.personnel import AffectationPedagogique


async def purge_annee_scolaire(db: AsyncSession, annee_id: UUID) -> bool:
    """Supprime l'année et les données liées. Retourne False si l'année n'existe pas."""
    result = await db.execute(select(AnneeScolaire).where(AnneeScolaire.id == annee_id))
    annee = result.scalar_one_or_none()
    if annee is None:
        return False

    aid = annee_id
    paiement_ids = select(Paiement.id).where(Paiement.annee_scolaire_id == aid)

    await db.execute(
        delete(HistoriquePaiement).where(
            (HistoriquePaiement.annee_scolaire_id == aid) | HistoriquePaiement.paiement_id.in_(paiement_ids)
        )
    )
    await db.execute(
        update(Paiement)
        .where(Paiement.annee_scolaire_id == aid)
        .values(paiement_origine_id=None)
    )
    await db.execute(delete(Paiement).where(Paiement.annee_scolaire_id == aid))
    await db.execute(delete(RelanceImpaye).where(RelanceImpaye.annee_scolaire_id == aid))
    await db.execute(delete(RemiseEleve).where(RemiseEleve.annee_scolaire_id == aid))
    await db.execute(delete(SequenceRecu).where(SequenceRecu.annee_scolaire_id == aid))
    await db.execute(delete(TarifNiveau).where(TarifNiveau.annee_scolaire_id == aid))
    await db.execute(delete(TrancheFrais).where(TrancheFrais.annee_scolaire_id == aid))

    await db.execute(delete(SeanceCours).where(SeanceCours.annee_scolaire_id == aid))
    await db.execute(delete(CreneauHoraire).where(CreneauHoraire.annee_scolaire_id == aid))
    await db.execute(delete(AffectationPedagogique).where(AffectationPedagogique.annee_scolaire_id == aid))
    await db.execute(delete(Inscription).where(Inscription.annee_scolaire_id == aid))

    await db.execute(delete(Depense).where(Depense.annee_scolaire_id == aid))
    await db.execute(delete(BudgetLigne).where(BudgetLigne.annee_scolaire_id == aid))
    await db.execute(delete(EcritureComptable).where(EcritureComptable.annee_scolaire_id == aid))

    await db.execute(delete(CalendrierScolaire).where(CalendrierScolaire.annee_scolaire_id == aid))
    await db.execute(delete(Periode).where(Periode.annee_scolaire_id == aid))
    await db.execute(delete(Classe).where(Classe.annee_scolaire_id == aid))
    await db.execute(delete(Bareme).where(Bareme.annee_scolaire_id == aid))

    inscrits = select(Inscription.eleve_id).distinct()
    await db.execute(delete(Eleve).where(Eleve.id.not_in(inscrits)))

    await db.execute(delete(AnneeScolaire).where(AnneeScolaire.id == aid))
    await db.flush()
    return True


async def purge_annee_scolaire_by_libelle(db: AsyncSession, libelle: str) -> bool:
    result = await db.execute(select(AnneeScolaire.id).where(AnneeScolaire.libelle == libelle))
    annee_id = result.scalar_one_or_none()
    if annee_id is None:
        return False
    return await purge_annee_scolaire(db, annee_id)


async def activer_annee_by_libelle(db: AsyncSession, libelle: str) -> AnneeScolaire | None:
    result = await db.execute(select(AnneeScolaire).where(AnneeScolaire.libelle == libelle))
    annee = result.scalar_one_or_none()
    if annee is None:
        return None
    await db.execute(update(AnneeScolaire).values(is_active=False))
    annee.is_active = True
    annee.statut = StatutAnneeScolaire.ACTIVE.value
    await db.flush()
    return annee
