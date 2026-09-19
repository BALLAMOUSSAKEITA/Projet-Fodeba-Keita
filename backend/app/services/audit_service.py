from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog, HistoriqueNote, HistoriquePaiement
from app.schemas.securite import (
    AuditLogResponse,
    HistoriqueNoteResponse,
    HistoriquePaiementResponse,
)


async def log_audit(
    db: AsyncSession,
    *,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: str | None = None,
    user_id: UUID | None = None,
    user_email: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )


async def list_audit_logs(
    db: AsyncSession,
    limit: int = 100,
    resource_type: str | None = None,
    action: str | None = None,
) -> list[AuditLogResponse]:
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(min(limit, 500))
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if action:
        query = query.where(AuditLog.action == action)
    result = await db.execute(query)
    return [AuditLogResponse.model_validate(r) for r in result.scalars().all()]


async def list_historique_notes(
    db: AsyncSession,
    eleve_id: UUID | None = None,
    limit: int = 100,
) -> list[HistoriqueNoteResponse]:
    query = select(HistoriqueNote).order_by(HistoriqueNote.created_at.desc()).limit(min(limit, 500))
    if eleve_id:
        query = query.where(HistoriqueNote.eleve_id == eleve_id)
    result = await db.execute(query)
    items = []
    for h in result.scalars().all():
        items.append(
            HistoriqueNoteResponse(
                id=h.id,
                evaluation_id=h.evaluation_id,
                eleve_id=h.eleve_id,
                annee_scolaire_id=h.annee_scolaire_id,
                ancienne_valeur=str(h.ancienne_valeur) if h.ancienne_valeur is not None else None,
                nouvelle_valeur=str(h.nouvelle_valeur) if h.nouvelle_valeur is not None else None,
                ancien_absent=h.ancien_absent,
                nouveau_absent=h.nouveau_absent,
                modifie_par_id=h.modifie_par_id,
                ip_address=h.ip_address,
                created_at=h.created_at,
            )
        )
    return items


async def list_historique_paiements(
    db: AsyncSession,
    eleve_id: UUID | None = None,
    limit: int = 100,
) -> list[HistoriquePaiementResponse]:
    query = select(HistoriquePaiement).order_by(HistoriquePaiement.created_at.desc()).limit(min(limit, 500))
    if eleve_id:
        query = query.where(HistoriquePaiement.eleve_id == eleve_id)
    result = await db.execute(query)
    items = []
    for h in result.scalars().all():
        items.append(
            HistoriquePaiementResponse(
                id=h.id,
                paiement_id=h.paiement_id,
                eleve_id=h.eleve_id,
                annee_scolaire_id=h.annee_scolaire_id,
                action=h.action,
                montant=str(h.montant),
                statut_avant=h.statut_avant,
                statut_apres=h.statut_apres,
                details=h.details,
                modifie_par_id=h.modifie_par_id,
                ip_address=h.ip_address,
                created_at=h.created_at,
            )
        )
    return items
