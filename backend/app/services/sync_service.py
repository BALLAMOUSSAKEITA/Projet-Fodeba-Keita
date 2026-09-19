from datetime import UTC, date, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.notes import Note
from app.models.paiements import Paiement
from app.models.parametrage import Classe
from app.models.presences import AppelPresence, PresenceEleve
from app.schemas.notes import NotesBulkUpdate
from app.schemas.paiements import PaiementCreate
from app.schemas.presences import AppelBulkUpdate
from app.schemas.sync import (
    SyncClasseItem,
    SyncConflictDetail,
    SyncNoteChange,
    SyncPaiementChange,
    SyncPresenceChange,
    SyncPullResponse,
    SyncPushItem,
    SyncPushResponse,
    SyncPushResultItem,
)
from app.services import eleve_service, notes_service, paiements_service, parametrage_service, presences_service


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _has_conflict(server_updated_at: datetime, client_updated_at: datetime, strategy: str) -> bool:
    server_ts = _ensure_utc(server_updated_at).timestamp()
    client_ts = _ensure_utc(client_updated_at).timestamp()
    if server_ts <= client_ts:
        return False
    return strategy != "client_wins"


async def pull_offline_bundle(
    db: AsyncSession,
    since: datetime | None = None,
) -> SyncPullResponse:
    items, total = await eleve_service.list_eleves(db, skip=0, limit=500, statut="actif")

    annee = await parametrage_service.get_annee_active(db)
    classes_query = select(Classe).options(selectinload(Classe.niveau)).order_by(Classe.nom)
    if annee:
        classes_query = classes_query.where(Classe.annee_scolaire_id == annee.id)
    classes_result = await db.execute(classes_query)
    classes = [
        SyncClasseItem(
            id=c.id,
            nom=c.nom,
            capacite_max=c.capacite_max,
            salle=c.salle,
            niveau_code=c.niveau.code if c.niveau else None,
        )
        for c in classes_result.scalars().all()
    ]

    notes_changes: list[SyncNoteChange] = []
    presences_changes: list[SyncPresenceChange] = []
    paiements_changes: list[SyncPaiementChange] = []

    if since is not None:
        notes_result = await db.execute(
            select(Note).where(Note.updated_at >= since).order_by(Note.updated_at)
        )
        for note in notes_result.scalars().all():
            notes_changes.append(
                SyncNoteChange(
                    id=note.id,
                    evaluation_id=note.evaluation_id,
                    eleve_id=note.eleve_id,
                    valeur=note.valeur,
                    is_absent=note.is_absent,
                    updated_at=note.updated_at,
                )
            )

        pres_result = await db.execute(
            select(PresenceEleve, AppelPresence)
            .join(AppelPresence, AppelPresence.id == PresenceEleve.appel_id)
            .where(PresenceEleve.updated_at >= since)
            .order_by(PresenceEleve.updated_at)
        )
        for presence, appel in pres_result.all():
            presences_changes.append(
                SyncPresenceChange(
                    id=presence.id,
                    appel_id=appel.id,
                    classe_id=appel.classe_id,
                    appel_date=appel.date,
                    eleve_id=presence.eleve_id,
                    statut=presence.statut,
                    updated_at=presence.updated_at,
                )
            )

        paiements_result = await db.execute(
            select(Paiement).where(Paiement.updated_at >= since).order_by(Paiement.updated_at)
        )
        for p in paiements_result.scalars().all():
            paiements_changes.append(
                SyncPaiementChange(
                    id=p.id,
                    eleve_id=p.eleve_id,
                    type_frais_id=p.type_frais_id,
                    montant=p.montant,
                    mode_paiement=p.mode_paiement,
                    numero_recu=p.numero_recu,
                    statut=p.statut,
                    updated_at=p.updated_at,
                )
            )

    return SyncPullResponse(
        server_time=_utc_now(),
        eleves=items,
        eleves_total=total,
        classes=classes,
        notes_changes=notes_changes,
        presences_changes=presences_changes,
        paiements_changes=paiements_changes,
    )


async def _get_notes_server_updated_at(db: AsyncSession, evaluation_id: UUID) -> datetime | None:
    result = await db.execute(
        select(func.max(Note.updated_at), func.max(Note.created_at)).where(
            Note.evaluation_id == evaluation_id
        )
    )
    updated_at, created_at = result.one()
    return updated_at or created_at


async def _get_appel_server_updated_at(
    db: AsyncSession,
    classe_id: UUID,
    appel_date: date,
) -> datetime | None:
    result = await db.execute(
        select(AppelPresence.updated_at).where(
            AppelPresence.classe_id == classe_id,
            AppelPresence.date == appel_date,
        )
    )
    return result.scalar_one_or_none()


async def _process_notes(
    db: AsyncSession,
    item: SyncPushItem,
    user_id: UUID | None,
    ip_address: str | None,
    user_email: str | None,
) -> SyncPushResultItem:
    evaluation_id = UUID(item.payload["evaluation_id"])
    data = NotesBulkUpdate.model_validate(item.payload["data"])

    server_updated_at = await _get_notes_server_updated_at(db, evaluation_id)
    if server_updated_at and _has_conflict(server_updated_at, item.client_updated_at, item.resolve_strategy):
        return SyncPushResultItem(
            client_id=item.client_id,
            status="conflict",
            entity_type="notes",
            conflict=SyncConflictDetail(
                entity_type="notes",
                server_updated_at=server_updated_at,
                client_updated_at=item.client_updated_at,
                server_snapshot={"evaluation_id": str(evaluation_id), "server_updated_at": server_updated_at.isoformat()},
            ),
            message="Des notes plus récentes existent sur le serveur",
        )

    result = await notes_service.bulk_update_notes(
        db,
        evaluation_id,
        data,
        user_id=user_id,
        ip_address=ip_address,
        user_email=user_email,
    )
    return SyncPushResultItem(
        client_id=item.client_id,
        status="applied",
        entity_type="notes",
        server_id=str(result.evaluation.id),
        message="Notes synchronisées",
    )


async def _process_presence(
    db: AsyncSession,
    item: SyncPushItem,
    user_id: UUID | None,
) -> SyncPushResultItem:
    classe_id = UUID(item.payload["classe_id"])
    appel_date = date.fromisoformat(item.payload["appel_date"])
    data = AppelBulkUpdate.model_validate(item.payload["data"])

    server_updated_at = await _get_appel_server_updated_at(db, classe_id, appel_date)
    if server_updated_at and _has_conflict(server_updated_at, item.client_updated_at, item.resolve_strategy):
        return SyncPushResultItem(
            client_id=item.client_id,
            status="conflict",
            entity_type="presence",
            conflict=SyncConflictDetail(
                entity_type="presence",
                server_updated_at=server_updated_at,
                client_updated_at=item.client_updated_at,
                server_snapshot={
                    "classe_id": str(classe_id),
                    "appel_date": appel_date.isoformat(),
                    "server_updated_at": server_updated_at.isoformat(),
                },
            ),
            message="Un appel plus récent existe sur le serveur",
        )

    result = await presences_service.save_appel(db, classe_id, appel_date, data, user_id)
    return SyncPushResultItem(
        client_id=item.client_id,
        status="applied",
        entity_type="presence",
        server_id=str(result.appel_id) if result.appel_id else None,
        message="Présences synchronisées",
    )


async def _process_paiement(
    db: AsyncSession,
    item: SyncPushItem,
    user_id: UUID | None,
    ip_address: str | None,
    user_email: str | None,
) -> SyncPushResultItem:
    payload = dict(item.payload)
    offline_ref = f"offline:{item.client_id}"
    existing = await db.execute(
        select(Paiement).where(Paiement.reference_externe == offline_ref)
    )
    dup = existing.scalar_one_or_none()
    if dup:
        return SyncPushResultItem(
            client_id=item.client_id,
            status="duplicate",
            entity_type="paiement",
            server_id=str(dup.id),
            message="Paiement déjà synchronisé",
        )

    payload.setdefault("reference_externe", offline_ref)
    data = PaiementCreate.model_validate(payload)

    result = await paiements_service.create_paiement(
        db,
        data,
        user_id=user_id,
        ip_address=ip_address,
        user_email=user_email,
    )
    return SyncPushResultItem(
        client_id=item.client_id,
        status="applied",
        entity_type="paiement",
        server_id=str(result.id),
        message="Paiement synchronisé",
    )


async def push_batch(
    db: AsyncSession,
    operations: list[SyncPushItem],
    user_id: UUID | None = None,
    ip_address: str | None = None,
    user_email: str | None = None,
) -> SyncPushResponse:
    results: list[SyncPushResultItem] = []
    applied = conflicts = errors = 0

    for item in operations:
        try:
            if item.entity_type == "notes":
                result = await _process_notes(db, item, user_id, ip_address, user_email)
            elif item.entity_type == "presence":
                result = await _process_presence(db, item, user_id)
            elif item.entity_type == "paiement":
                result = await _process_paiement(db, item, user_id, ip_address, user_email)
            else:
                result = SyncPushResultItem(
                    client_id=item.client_id,
                    status="error",
                    entity_type=item.entity_type,
                    message="Type d'entité non supporté",
                )
        except HTTPException as exc:
            result = SyncPushResultItem(
                client_id=item.client_id,
                status="error",
                entity_type=item.entity_type,
                message=str(exc.detail),
            )
        except Exception as exc:
            result = SyncPushResultItem(
                client_id=item.client_id,
                status="error",
                entity_type=item.entity_type,
                message=str(exc),
            )

        results.append(result)
        if result.status == "applied" or result.status == "duplicate":
            applied += 1
        elif result.status == "conflict":
            conflicts += 1
        else:
            errors += 1

    return SyncPushResponse(results=results, applied=applied, conflicts=conflicts, errors=errors)
