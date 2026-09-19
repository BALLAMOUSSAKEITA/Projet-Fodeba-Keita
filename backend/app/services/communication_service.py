from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.communication import (
    Annonce,
    AudienceAnnonce,
    HistoriqueCommunication,
    ModeleMessage,
    StatutAnnonce,
    StatutEnvoi,
)
from app.models.user import User
from app.schemas.communication import (
    AnnonceCreate,
    AnnonceResponse,
    EnvoiMessageCreate,
    HistoriqueResponse,
    ModeleMessageCreate,
    ModeleMessageResponse,
)
from app.services import parametrage_service


async def _annonce_to_response(db: AsyncSession, annonce: Annonce) -> AnnonceResponse:
    auteur_nom = None
    if annonce.auteur_id:
        auteur = await db.get(User, annonce.auteur_id)
        if auteur:
            auteur_nom = f"{auteur.prenom} {auteur.nom}"
    return AnnonceResponse(
        id=annonce.id,
        titre=annonce.titre,
        contenu=annonce.contenu,
        audience=annonce.audience,
        statut=annonce.statut,
        date_publication=annonce.date_publication,
        date_expiration=annonce.date_expiration,
        auteur_nom=auteur_nom,
    )


async def list_annonces(
    db: AsyncSession,
    audience: str | None = None,
    publiees_seulement: bool = False,
) -> list[AnnonceResponse]:
    query = select(Annonce).order_by(Annonce.date_publication.desc().nullslast(), Annonce.created_at.desc())
    if publiees_seulement:
        today = date.today()
        query = query.where(
            Annonce.statut == StatutAnnonce.PUBLIEE.value,
            or_(Annonce.date_expiration.is_(None), Annonce.date_expiration >= today),
        )
    if audience:
        query = query.where(
            or_(
                Annonce.audience == AudienceAnnonce.TOUS.value,
                Annonce.audience == audience,
            )
        )
    result = await db.execute(query)
    return [await _annonce_to_response(db, a) for a in result.scalars().all()]


async def create_annonce(
    db: AsyncSession,
    data: AnnonceCreate,
    user_id: UUID,
    publier: bool = False,
) -> AnnonceResponse:
    annee_id = data.annee_scolaire_id
    if annee_id is None:
        annee = await parametrage_service.get_annee_active(db)
        annee_id = annee.id if annee else None

    annonce = Annonce(
        titre=data.titre,
        contenu=data.contenu,
        audience=data.audience,
        statut=StatutAnnonce.PUBLIEE.value if publier else StatutAnnonce.BROUILLON.value,
        date_publication=date.today() if publier else None,
        date_expiration=data.date_expiration,
        auteur_id=user_id,
        annee_scolaire_id=annee_id,
    )
    db.add(annonce)
    await db.commit()
    await db.refresh(annonce)
    return await _annonce_to_response(db, annonce)


async def publier_annonce(db: AsyncSession, annonce_id: UUID) -> AnnonceResponse:
    annonce = await db.get(Annonce, annonce_id)
    if annonce is None:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    annonce.statut = StatutAnnonce.PUBLIEE.value
    annonce.date_publication = date.today()
    await db.commit()
    return await _annonce_to_response(db, annonce)


async def archiver_annonce(db: AsyncSession, annonce_id: UUID) -> AnnonceResponse:
    annonce = await db.get(Annonce, annonce_id)
    if annonce is None:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    annonce.statut = StatutAnnonce.ARCHIVEE.value
    await db.commit()
    return await _annonce_to_response(db, annonce)


async def list_modeles(db: AsyncSession) -> list[ModeleMessageResponse]:
    result = await db.execute(
        select(ModeleMessage).where(ModeleMessage.actif.is_(True)).order_by(ModeleMessage.libelle)
    )
    return [ModeleMessageResponse.model_validate(m) for m in result.scalars().all()]


async def create_modele(db: AsyncSession, data: ModeleMessageCreate) -> ModeleMessageResponse:
    existing = await db.execute(select(ModeleMessage).where(ModeleMessage.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Code modèle déjà utilisé")
    modele = ModeleMessage(**data.model_dump())
    db.add(modele)
    await db.commit()
    await db.refresh(modele)
    return ModeleMessageResponse.model_validate(modele)


async def envoyer_message(
    db: AsyncSession,
    data: EnvoiMessageCreate,
    user_id: UUID,
) -> HistoriqueResponse:
    sujet = data.sujet
    corps = data.corps
    canal = data.canal

    if data.modele_id:
        modele = await db.get(ModeleMessage, data.modele_id)
        if modele is None:
            raise HTTPException(status_code=404, detail="Modèle introuvable")
        sujet = modele.sujet
        corps = modele.corps
        canal = modele.canal

    entry = HistoriqueCommunication(
        modele_id=data.modele_id,
        canal=canal,
        destinataire=data.destinataire,
        sujet=sujet,
        corps=corps,
        statut=StatutEnvoi.SIMULE.value,
        envoye_par_id=user_id,
        eleve_id=data.eleve_id,
        envoye_le=datetime.now(timezone.utc),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return HistoriqueResponse.model_validate(entry)


async def list_historique(
    db: AsyncSession,
    limit: int = 50,
) -> list[HistoriqueResponse]:
    result = await db.execute(
        select(HistoriqueCommunication)
        .order_by(HistoriqueCommunication.envoye_le.desc().nullslast(), HistoriqueCommunication.created_at.desc())
        .limit(limit)
    )
    return [HistoriqueResponse.model_validate(h) for h in result.scalars().all()]
