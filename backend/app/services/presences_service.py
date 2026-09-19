from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.eleve import Eleve
from app.models.parametrage import Classe
from app.models.personnel import CongeAbsence, Personnel, StatutConge
from app.models.presences import (
    AppelPresence,
    IncidentDisciplinaire,
    PresenceEleve,
    StatutJustification,
    StatutPresence,
)
from app.schemas.presences import (
    AppelBulkUpdate,
    AppelPresenceResponse,
    ClasseRecapResponse,
    EleveRecapItem,
    EleveRecapResponse,
    EnseignantAbsenceItem,
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    JustificationReview,
    JustificationUpdate,
    PresenceEleveRow,
)
from app.services import classe_service


async def _get_classe_or_404(db: AsyncSession, classe_id: UUID) -> Classe:
    result = await db.execute(
        select(Classe).where(Classe.id == classe_id)
    )
    classe = result.scalar_one_or_none()
    if classe is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")
    return classe


async def _get_or_create_appel(
    db: AsyncSession,
    classe_id: UUID,
    appel_date: date,
    user_id: UUID | None = None,
) -> AppelPresence:
    result = await db.execute(
        select(AppelPresence)
        .options(selectinload(AppelPresence.presences))
        .where(AppelPresence.classe_id == classe_id, AppelPresence.date == appel_date)
    )
    appel = result.scalar_one_or_none()
    if appel is None:
        appel = AppelPresence(classe_id=classe_id, date=appel_date, saisi_par_id=user_id)
        db.add(appel)
        await db.flush()
    return appel


async def get_appel(
    db: AsyncSession,
    classe_id: UUID,
    appel_date: date,
) -> AppelPresenceResponse:
    classe = await _get_classe_or_404(db, classe_id)
    eleves_data = await classe_service.list_eleves_classe(db, classe_id)

    result = await db.execute(
        select(AppelPresence)
        .options(selectinload(AppelPresence.presences))
        .where(AppelPresence.classe_id == classe_id, AppelPresence.date == appel_date)
    )
    appel = result.scalar_one_or_none()
    pres_map = {p.eleve_id: p for p in (appel.presences if appel else [])}

    rows = [
        PresenceEleveRow(
            presence_id=pres_map[e.id].id if e.id in pres_map else None,
            eleve_id=e.id,
            matricule=e.matricule,
            nom=e.nom,
            prenoms=e.prenoms,
            statut=pres_map[e.id].statut if e.id in pres_map else StatutPresence.PRESENT.value,
            retard_minutes=pres_map[e.id].retard_minutes if e.id in pres_map else None,
            motif=pres_map[e.id].motif if e.id in pres_map else None,
            justification=pres_map[e.id].justification if e.id in pres_map else None,
            justification_statut=pres_map[e.id].justification_statut if e.id in pres_map else None,
        )
        for e in eleves_data.eleves
    ]

    return AppelPresenceResponse(
        appel_id=appel.id if appel else None,
        classe_id=classe_id,
        classe_nom=classe.nom,
        date=appel_date,
        remarque=appel.remarque if appel else None,
        eleves=rows,
    )


async def save_appel(
    db: AsyncSession,
    classe_id: UUID,
    appel_date: date,
    data: AppelBulkUpdate,
    user_id: UUID | None = None,
) -> AppelPresenceResponse:
    await _get_classe_or_404(db, classe_id)
    eleves_data = await classe_service.list_eleves_classe(db, classe_id)
    eleve_ids = {e.id for e in eleves_data.eleves}

    appel = await _get_or_create_appel(db, classe_id, appel_date, user_id)
    if user_id:
        appel.saisi_par_id = user_id
    appel.remarque = data.remarque

    pres_result = await db.execute(
        select(PresenceEleve).where(PresenceEleve.appel_id == appel.id)
    )
    existing = {p.eleve_id: p for p in pres_result.scalars().all()}

    for item in data.presences:
        if item.eleve_id not in eleve_ids:
            raise HTTPException(status_code=400, detail="Élève hors de la classe")
        retard = item.retard_minutes
        if item.statut == StatutPresence.RETARD.value and retard is None:
            retard = 15

        just_statut = None
        if item.statut in (StatutPresence.ABSENT.value, StatutPresence.RETARD.value):
            if item.eleve_id in existing and existing[item.eleve_id].justification_statut:
                just_statut = existing[item.eleve_id].justification_statut
            elif item.motif:
                just_statut = StatutJustification.EN_ATTENTE.value

        if item.eleve_id in existing:
            p = existing[item.eleve_id]
            p.statut = item.statut
            p.retard_minutes = retard if item.statut == StatutPresence.RETARD.value else None
            if item.motif is not None:
                p.motif = item.motif
                if item.motif and p.justification_statut is None:
                    p.justification_statut = StatutJustification.EN_ATTENTE.value
        else:
            db.add(
                PresenceEleve(
                    appel_id=appel.id,
                    eleve_id=item.eleve_id,
                    statut=item.statut,
                    retard_minutes=retard if item.statut == StatutPresence.RETARD.value else None,
                    motif=item.motif,
                    justification_statut=just_statut,
                )
            )

    await db.commit()
    return await get_appel(db, classe_id, appel_date)


async def submit_justification(
    db: AsyncSession,
    presence_id: UUID,
    data: JustificationUpdate,
) -> PresenceEleveRow:
    result = await db.execute(
        select(PresenceEleve)
        .options(selectinload(PresenceEleve.appel))
        .where(PresenceEleve.id == presence_id)
    )
    presence = result.scalar_one_or_none()
    if presence is None:
        raise HTTPException(status_code=404, detail="Présence introuvable")
    if presence.statut not in (StatutPresence.ABSENT.value, StatutPresence.RETARD.value):
        raise HTTPException(status_code=422, detail="Justification non applicable")

    presence.justification = data.justification
    if data.accepter:
        presence.justification_statut = StatutJustification.ACCEPTEE.value
        if presence.statut == StatutPresence.ABSENT.value:
            presence.statut = StatutPresence.EXCUSE.value
    else:
        presence.justification_statut = StatutJustification.EN_ATTENTE.value

    await db.commit()

    eleve = await db.get(Eleve, presence.eleve_id)
    return PresenceEleveRow(
        presence_id=presence.id,
        eleve_id=presence.eleve_id,
        matricule=eleve.matricule if eleve else "",
        nom=eleve.nom if eleve else "",
        prenoms=eleve.prenoms if eleve else "",
        statut=presence.statut,
        retard_minutes=presence.retard_minutes,
        motif=presence.motif,
        justification=presence.justification,
        justification_statut=presence.justification_statut,
    )


async def review_justification(
    db: AsyncSession,
    presence_id: UUID,
    data: JustificationReview,
) -> PresenceEleveRow:
    result = await db.execute(select(PresenceEleve).where(PresenceEleve.id == presence_id))
    presence = result.scalar_one_or_none()
    if presence is None:
        raise HTTPException(status_code=404, detail="Présence introuvable")

    presence.justification_statut = data.statut
    if data.statut == StatutJustification.ACCEPTEE.value and presence.statut == StatutPresence.ABSENT.value:
        presence.statut = StatutPresence.EXCUSE.value

    await db.commit()
    eleve = await db.get(Eleve, presence.eleve_id)
    return PresenceEleveRow(
        presence_id=presence.id,
        eleve_id=presence.eleve_id,
        matricule=eleve.matricule if eleve else "",
        nom=eleve.nom if eleve else "",
        prenoms=eleve.prenoms if eleve else "",
        statut=presence.statut,
        retard_minutes=presence.retard_minutes,
        motif=presence.motif,
        justification=presence.justification,
        justification_statut=presence.justification_statut,
    )


def _aggregate_presences(
    presences: list[PresenceEleve],
) -> dict[UUID, EleveRecapItem]:
    stats: dict[UUID, dict] = {}

    for p in presences:
        if p.eleve_id not in stats:
            stats[p.eleve_id] = {
                "jours_absents": 0,
                "jours_retards": 0,
                "minutes_retard_total": 0,
                "jours_excuses": 0,
                "absences_non_justifiees": 0,
            }
        s = stats[p.eleve_id]
        if p.statut == StatutPresence.ABSENT.value:
            s["jours_absents"] += 1
            if p.justification_statut != StatutJustification.ACCEPTEE.value:
                s["absences_non_justifiees"] += 1
        elif p.statut == StatutPresence.EXCUSE.value:
            s["jours_excuses"] += 1
        elif p.statut == StatutPresence.RETARD.value:
            s["jours_retards"] += 1
            s["minutes_retard_total"] += p.retard_minutes or 0

    return stats


async def get_classe_recap(
    db: AsyncSession,
    classe_id: UUID,
    date_debut: date,
    date_fin: date,
) -> ClasseRecapResponse:
    classe = await _get_classe_or_404(db, classe_id)
    eleves_data = await classe_service.list_eleves_classe(db, classe_id)

    result = await db.execute(
        select(PresenceEleve)
        .join(AppelPresence, AppelPresence.id == PresenceEleve.appel_id)
        .where(
            AppelPresence.classe_id == classe_id,
            AppelPresence.date >= date_debut,
            AppelPresence.date <= date_fin,
        )
    )
    presences = list(result.scalars().all())
    stats = _aggregate_presences(presences)

    items: list[EleveRecapItem] = []
    for e in eleves_data.eleves:
        s = stats.get(e.id, {
            "jours_absents": 0,
            "jours_retards": 0,
            "minutes_retard_total": 0,
            "jours_excuses": 0,
            "absences_non_justifiees": 0,
        })
        items.append(
            EleveRecapItem(
                eleve_id=e.id,
                matricule=e.matricule,
                nom=e.nom,
                prenoms=e.prenoms,
                **s,
            )
        )

    return ClasseRecapResponse(
        classe_id=classe_id,
        classe_nom=classe.nom,
        date_debut=date_debut,
        date_fin=date_fin,
        effectif=len(eleves_data.eleves),
        eleves=items,
    )


async def get_eleve_recap(
    db: AsyncSession,
    eleve_id: UUID,
    date_debut: date,
    date_fin: date,
) -> EleveRecapResponse:
    eleve = await db.get(Eleve, eleve_id)
    if eleve is None:
        raise HTTPException(status_code=404, detail="Élève introuvable")

    result = await db.execute(
        select(PresenceEleve)
        .join(AppelPresence, AppelPresence.id == PresenceEleve.appel_id)
        .where(
            PresenceEleve.eleve_id == eleve_id,
            AppelPresence.date >= date_debut,
            AppelPresence.date <= date_fin,
        )
    )
    presences = list(result.scalars().all())
    stats = _aggregate_presences(presences)
    s = stats.get(eleve_id, {
        "jours_absents": 0,
        "jours_retards": 0,
        "minutes_retard_total": 0,
        "jours_excuses": 0,
        "absences_non_justifiees": 0,
    })

    inc_result = await db.execute(
        select(func.count())
        .select_from(IncidentDisciplinaire)
        .where(
            IncidentDisciplinaire.eleve_id == eleve_id,
            IncidentDisciplinaire.date >= date_debut,
            IncidentDisciplinaire.date <= date_fin,
        )
    )
    incidents_count = inc_result.scalar_one()

    return EleveRecapResponse(
        eleve_id=eleve.id,
        matricule=eleve.matricule,
        nom=eleve.nom,
        prenoms=eleve.prenoms,
        date_debut=date_debut,
        date_fin=date_fin,
        incidents_count=incidents_count,
        **s,
    )


async def list_enseignants_absences(
    db: AsyncSession,
    target_date: date,
) -> list[EnseignantAbsenceItem]:
    result = await db.execute(
        select(CongeAbsence, Personnel)
        .join(Personnel, Personnel.id == CongeAbsence.personnel_id)
        .where(
            Personnel.categorie == "enseignant",
            CongeAbsence.statut == StatutConge.APPROUVE.value,
            CongeAbsence.date_debut <= target_date,
            CongeAbsence.date_fin >= target_date,
        )
        .order_by(Personnel.nom)
    )
    items: list[EnseignantAbsenceItem] = []
    for conge, pers in result.all():
        items.append(
            EnseignantAbsenceItem(
                personnel_id=pers.id,
                matricule=pers.matricule,
                nom=pers.nom,
                prenoms=pers.prenoms,
                type_conge=conge.type,
                date_debut=conge.date_debut,
                date_fin=conge.date_fin,
                statut=conge.statut,
            )
        )
    return items


async def list_incidents(
    db: AsyncSession,
    classe_id: UUID | None = None,
    eleve_id: UUID | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[IncidentResponse]:
    query = (
        select(IncidentDisciplinaire, Eleve, Classe)
        .join(Eleve, Eleve.id == IncidentDisciplinaire.eleve_id)
        .outerjoin(Classe, Classe.id == IncidentDisciplinaire.classe_id)
        .order_by(IncidentDisciplinaire.date.desc())
        .offset(skip)
        .limit(limit)
    )
    if classe_id:
        query = query.where(IncidentDisciplinaire.classe_id == classe_id)
    if eleve_id:
        query = query.where(IncidentDisciplinaire.eleve_id == eleve_id)

    result = await db.execute(query)
    return [
        IncidentResponse(
            id=inc.id,
            eleve_id=inc.eleve_id,
            eleve_nom=eleve.nom,
            eleve_prenoms=eleve.prenoms,
            classe_id=inc.classe_id,
            classe_nom=classe.nom if classe else None,
            date=inc.date,
            type=inc.type,
            description=inc.description,
            sanction=inc.sanction,
        )
        for inc, eleve, classe in result.all()
    ]


async def create_incident(
    db: AsyncSession,
    data: IncidentCreate,
    user_id: UUID | None = None,
) -> IncidentResponse:
    eleve = await db.get(Eleve, data.eleve_id)
    if eleve is None:
        raise HTTPException(status_code=404, detail="Élève introuvable")

    inc = IncidentDisciplinaire(
        eleve_id=data.eleve_id,
        classe_id=data.classe_id,
        date=data.date,
        type=data.type,
        description=data.description,
        sanction=data.sanction,
        saisi_par_id=user_id,
    )
    db.add(inc)
    await db.commit()
    await db.refresh(inc)

    classe_nom = None
    if data.classe_id:
        classe = await db.get(Classe, data.classe_id)
        classe_nom = classe.nom if classe else None

    return IncidentResponse(
        id=inc.id,
        eleve_id=inc.eleve_id,
        eleve_nom=eleve.nom,
        eleve_prenoms=eleve.prenoms,
        classe_id=inc.classe_id,
        classe_nom=classe_nom,
        date=inc.date,
        type=inc.type,
        description=inc.description,
        sanction=inc.sanction,
    )


async def update_incident(
    db: AsyncSession,
    incident_id: UUID,
    data: IncidentUpdate,
) -> IncidentResponse:
    result = await db.execute(
        select(IncidentDisciplinaire).where(IncidentDisciplinaire.id == incident_id)
    )
    inc = result.scalar_one_or_none()
    if inc is None:
        raise HTTPException(status_code=404, detail="Incident introuvable")

    if data.type is not None:
        inc.type = data.type
    if data.description is not None:
        inc.description = data.description
    if data.sanction is not None:
        inc.sanction = data.sanction

    await db.commit()
    eleve = await db.get(Eleve, inc.eleve_id)
    classe_nom = None
    if inc.classe_id:
        classe = await db.get(Classe, inc.classe_id)
        classe_nom = classe.nom if classe else None

    return IncidentResponse(
        id=inc.id,
        eleve_id=inc.eleve_id,
        eleve_nom=eleve.nom if eleve else "",
        eleve_prenoms=eleve.prenoms if eleve else "",
        classe_id=inc.classe_id,
        classe_nom=classe_nom,
        date=inc.date,
        type=inc.type,
        description=inc.description,
        sanction=inc.sanction,
    )


async def list_absences_a_justifier(
    db: AsyncSession,
    classe_id: UUID | None = None,
) -> list[PresenceEleveRow]:
    query = (
        select(PresenceEleve, Eleve)
        .join(Eleve, Eleve.id == PresenceEleve.eleve_id)
        .join(AppelPresence, AppelPresence.id == PresenceEleve.appel_id)
        .where(
            PresenceEleve.statut.in_([StatutPresence.ABSENT.value, StatutPresence.RETARD.value]),
            PresenceEleve.justification_statut == StatutJustification.EN_ATTENTE.value,
        )
        .order_by(AppelPresence.date.desc())
    )
    if classe_id:
        query = query.where(AppelPresence.classe_id == classe_id)

    result = await db.execute(query)
    return [
        PresenceEleveRow(
            presence_id=p.id,
            eleve_id=p.eleve_id,
            matricule=e.matricule,
            nom=e.nom,
            prenoms=e.prenoms,
            statut=p.statut,
            retard_minutes=p.retard_minutes,
            motif=p.motif,
            justification=p.justification,
            justification_statut=p.justification_statut,
        )
        for p, e in result.all()
    ]
