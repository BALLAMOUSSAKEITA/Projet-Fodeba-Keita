from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.paiements import Paiement
from app.models.parametrage import Classe
from app.schemas.paiements import PaiementCreate
from app.schemas.sync import (
    SyncClasseItem,
    SyncPaiementChange,
    SyncPullResponse,
    SyncPushItem,
    SyncPushResponse,
    SyncPushResultItem,
)
from app.services import eleve_service, paiements_service, parametrage_service


def _utc_now() -> datetime:
    return datetime.now(UTC)


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

    paiements_changes: list[SyncPaiementChange] = []

    if since is not None:
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
        paiements_changes=paiements_changes,
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
            if item.entity_type == "paiement":
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
