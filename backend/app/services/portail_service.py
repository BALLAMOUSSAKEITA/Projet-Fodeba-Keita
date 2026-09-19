from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.eleve import Eleve, Inscription, Tuteur
from app.models.parametrage import AnneeScolaire, Classe, Periode
from app.schemas.communication import (
    AnnonceResponse,
    EnfantItem,
    PeriodeNoteItem,
    PortailResumeResponse,
)
from app.services import (
    bulletin_service,
    communication_service,
    paiements_service,
    parametrage_service,
    presences_service,
)


async def _get_eleves_lies(db: AsyncSession, user_id: UUID) -> list[Eleve]:
    result = await db.execute(
        select(Eleve)
        .join(Tuteur, Tuteur.eleve_id == Eleve.id)
        .where(Tuteur.user_id == user_id)
        .distinct()
    )
    return list(result.scalars().all())


async def verify_acces_eleve(db: AsyncSession, user_id: UUID, eleve_id: UUID) -> Eleve:
    eleves = await _get_eleves_lies(db, user_id)
    eleve = next((e for e in eleves if e.id == eleve_id), None)
    if eleve is None:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cet élève")
    return eleve


async def _classe_eleve(db: AsyncSession, eleve_id: UUID, annee_id: UUID) -> str | None:
    result = await db.execute(
        select(Classe.nom)
        .join(Inscription, Inscription.classe_id == Classe.id)
        .where(Inscription.eleve_id == eleve_id, Inscription.annee_scolaire_id == annee_id)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_mes_enfants(db: AsyncSession, user_id: UUID) -> list[EnfantItem]:
    annee = await parametrage_service.get_annee_active(db)
    items: list[EnfantItem] = []
    for eleve in await _get_eleves_lies(db, user_id):
        classe_nom = await _classe_eleve(db, eleve.id, annee.id) if annee else None
        items.append(
            EnfantItem(
                eleve_id=eleve.id,
                matricule=eleve.matricule,
                nom=eleve.nom,
                prenoms=eleve.prenoms,
                classe_nom=classe_nom,
            )
        )
    return items


async def get_resume_enfant(db: AsyncSession, user_id: UUID, eleve_id: UUID) -> PortailResumeResponse:
    eleve = await verify_acces_eleve(db, user_id, eleve_id)
    annee = await parametrage_service.get_annee_active(db)
    if annee is None:
        raise HTTPException(status_code=404, detail="Année scolaire active introuvable")

    classe_nom = await _classe_eleve(db, eleve_id, annee.id)
    situation = await paiements_service.get_situation_eleve(db, eleve_id, annee.id)

    debut = annee.date_debut
    recap = await presences_service.get_eleve_recap(db, eleve_id, debut, date.today())

    periodes_result = await db.execute(
        select(Periode).where(Periode.annee_scolaire_id == annee.id).order_by(Periode.ordre)
    )
    periodes_notes: list[PeriodeNoteItem] = []
    for periode in periodes_result.scalars().all():
        try:
            bulletin = await bulletin_service.get_bulletin_data(db, eleve_id, periode.id)
            moy = bulletin.moyennes.moyenne_generale
            periodes_notes.append(
                PeriodeNoteItem(
                    periode_id=periode.id,
                    periode_libelle=periode.libelle,
                    moyenne_generale=str(moy) if moy is not None else None,
                    rang=bulletin.moyennes.rang,
                )
            )
        except HTTPException:
            continue

    annonces = await communication_service.list_annonces(
        db, audience="parents", publiees_seulement=True
    )

    return PortailResumeResponse(
        eleve_id=eleve.id,
        matricule=eleve.matricule,
        nom=eleve.nom,
        prenoms=eleve.prenoms,
        classe_nom=classe_nom,
        annee_libelle=annee.libelle,
        total_du=str(situation.total_du),
        total_paye=str(situation.total_paye),
        total_restant=str(situation.total_restant),
        jours_absents=recap.jours_absents,
        absences_non_justifiees=recap.absences_non_justifiees,
        jours_retards=recap.jours_retards,
        incidents_count=recap.incidents_count,
        periodes_notes=periodes_notes,
        annonces=annonces,
    )
