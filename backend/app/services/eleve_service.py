from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.eleve import (
    Eleve,
    Inscription,
    StatutEleve,
    Transfert,
    Tuteur,
    TypeInscription,
    TypeTransfert,
)
from app.models.parametrage import AnneeScolaire, Niveau
from app.schemas.eleve import (
    EffectifNiveauStat,
    EffectifStatsResponse,
    EleveCreate,
    EleveListItem,
    EleveUpdate,
    HistoriqueScolaireResponse,
    ReinscriptionRequest,
    TransfertEntrantCreate,
    TransfertSortantRequest,
    TuteurCreate,
    TuteurUpdate,
)
from app.services import classe_service, parametrage_service

NIVEAU_MATRICULE_MAP = {
    "PS": "PS",
    "MS": "MS",
    "GS": "GS",
    "1A": "P1",
    "2A": "P2",
    "3A": "P3",
    "4A": "P4",
    "5A": "P5",
    "6A": "P6",
}


async def generate_matricule(
    db: AsyncSession,
    niveau: Niveau,
    annee: AnneeScolaire,
) -> str:
    prefix_code = NIVEAU_MATRICULE_MAP.get(niveau.code, niveau.code)
    year = annee.date_debut.year
    pattern_prefix = f"{year}-{prefix_code}-"

    result = await db.execute(
        select(Eleve.matricule)
        .where(Eleve.matricule.like(f"{pattern_prefix}%"))
        .order_by(Eleve.matricule.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    seq = int(last.split("-")[-1]) + 1 if last else 1
    return f"{year}-{prefix_code}-{seq:04d}"


async def get_eleve(db: AsyncSession, eleve_id: UUID) -> Eleve:
    result = await db.execute(
        select(Eleve)
        .options(
            selectinload(Eleve.tuteurs),
            selectinload(Eleve.inscriptions).selectinload(Inscription.niveau),
            selectinload(Eleve.inscriptions).selectinload(Inscription.annee_scolaire),
            selectinload(Eleve.inscriptions).selectinload(Inscription.classe),
            selectinload(Eleve.transferts),
        )
        .where(Eleve.id == eleve_id)
    )
    eleve = result.scalar_one_or_none()
    if eleve is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Élève introuvable")
    return eleve


async def list_eleves(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
    sexe: str | None = None,
    niveau_id: UUID | None = None,
    classe_id: UUID | None = None,
    statut: str | None = None,
    annee_scolaire_id: UUID | None = None,
) -> tuple[list[EleveListItem], int]:
    annee = None
    if annee_scolaire_id:
        annee = await parametrage_service._get_annee(db, annee_scolaire_id)
    else:
        annee = await parametrage_service.get_annee_active(db)

    query = select(Eleve).distinct()

    if annee:
        query = query.join(Inscription, Inscription.eleve_id == Eleve.id).where(
            Inscription.annee_scolaire_id == annee.id
        )
        if niveau_id:
            query = query.where(Inscription.niveau_id == niveau_id)
        if classe_id:
            query = query.where(Inscription.classe_id == classe_id)

    if search:
        pattern = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(Eleve.nom).like(pattern),
                func.lower(Eleve.prenoms).like(pattern),
                func.lower(Eleve.matricule).like(pattern),
            )
        )

    if sexe:
        query = query.where(Eleve.sexe == sexe)

    if statut:
        query = query.where(Eleve.statut == statut)

    count_subq = query.subquery()
    total = (await db.execute(select(func.count()).select_from(count_subq))).scalar_one()

    result = await db.execute(
        query.options(
            selectinload(Eleve.inscriptions).selectinload(Inscription.niveau),
            selectinload(Eleve.inscriptions).selectinload(Inscription.classe),
        )
        .order_by(Eleve.nom, Eleve.prenoms)
        .offset(skip)
        .limit(limit)
    )
    eleves = list(result.scalars().unique().all())

    items: list[EleveListItem] = []
    for eleve in eleves:
        inscription = _get_inscription_for_annee(eleve, annee.id if annee else None)
        items.append(
            EleveListItem(
                id=eleve.id,
                matricule=eleve.matricule,
                nom=eleve.nom,
                prenoms=eleve.prenoms,
                sexe=eleve.sexe,
                date_naissance=eleve.date_naissance,
                statut=eleve.statut,
                niveau_libelle=inscription.niveau.libelle if inscription else None,
                niveau_code=inscription.niveau.code if inscription else None,
                classe_nom=inscription.classe.nom if inscription and inscription.classe else None,
            )
        )

    return items, total


def _get_inscription_for_annee(eleve: Eleve, annee_id: UUID | None) -> Inscription | None:
    if not annee_id:
        return eleve.inscriptions[0] if eleve.inscriptions else None
    for ins in eleve.inscriptions:
        if ins.annee_scolaire_id == annee_id:
            return ins
    return None


async def create_eleve(db: AsyncSession, data: EleveCreate) -> Eleve:
    annee = await parametrage_service.get_annee_active(db)
    if annee is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune année scolaire active. Configurez l'établissement d'abord.",
        )

    niveau = await parametrage_service._get_niveau(db, data.niveau_id)
    matricule = await generate_matricule(db, niveau, annee)

    eleve = Eleve(
        matricule=matricule,
        nom=data.nom.strip(),
        prenoms=data.prenoms.strip(),
        sexe=data.sexe,
        date_naissance=data.date_naissance,
        lieu_naissance=data.lieu_naissance,
        nationalite=data.nationalite,
        adresse=data.adresse,
        photo_url=data.photo_url,
        groupe_sanguin=data.groupe_sanguin,
        allergies=data.allergies,
        statut=StatutEleve.ACTIF.value,
    )
    db.add(eleve)
    await db.flush()

    for tuteur_data in data.tuteurs:
        db.add(Tuteur(eleve_id=eleve.id, **tuteur_data.model_dump()))

    db.add(
        Inscription(
            eleve_id=eleve.id,
            annee_scolaire_id=annee.id,
            niveau_id=niveau.id,
            type=TypeInscription.NOUVELLE.value,
            date_inscription=date.today(),
            statut=StatutEleve.ACTIF.value,
        )
    )
    await db.flush()
    return await get_eleve(db, eleve.id)


async def update_eleve(db: AsyncSession, eleve_id: UUID, data: EleveUpdate) -> Eleve:
    eleve = await get_eleve(db, eleve_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        if field in ("nom", "prenoms") and value:
            value = value.strip()
        setattr(eleve, field, value)
    await db.flush()
    return await get_eleve(db, eleve_id)


async def reinscrire_eleve(
    db: AsyncSession,
    eleve_id: UUID,
    data: ReinscriptionRequest,
) -> Eleve:
    eleve = await get_eleve(db, eleve_id)
    if eleve.statut != StatutEleve.ACTIF.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seuls les élèves actifs peuvent être réinscrits",
        )

    annee = await parametrage_service.get_annee_active(db)
    if data.annee_scolaire_id:
        annee = await parametrage_service._get_annee(db, data.annee_scolaire_id)
    if annee is None:
        raise HTTPException(status_code=400, detail="Année scolaire introuvable")

    await parametrage_service._get_niveau(db, data.niveau_id)

    existing = await db.execute(
        select(Inscription).where(
            Inscription.eleve_id == eleve_id,
            Inscription.annee_scolaire_id == annee.id,
        )
    )
    inscription = existing.scalar_one_or_none()
    if inscription:
        inscription.niveau_id = data.niveau_id
        inscription.type = TypeInscription.REINSCRIPTION.value
        inscription.date_inscription = date.today()
    else:
        db.add(
            Inscription(
                eleve_id=eleve.id,
                annee_scolaire_id=annee.id,
                niveau_id=data.niveau_id,
                type=TypeInscription.REINSCRIPTION.value,
                date_inscription=date.today(),
                statut=StatutEleve.ACTIF.value,
            )
        )
    await db.flush()
    return await get_eleve(db, eleve.id)


async def add_tuteur(db: AsyncSession, eleve_id: UUID, data: TuteurCreate) -> Eleve:
    await get_eleve(db, eleve_id)
    db.add(Tuteur(eleve_id=eleve_id, **data.model_dump()))
    await db.flush()
    return await get_eleve(db, eleve_id)


async def update_tuteur(
    db: AsyncSession,
    eleve_id: UUID,
    tuteur_id: UUID,
    data: TuteurUpdate,
) -> Eleve:
    result = await db.execute(
        select(Tuteur).where(Tuteur.id == tuteur_id, Tuteur.eleve_id == eleve_id)
    )
    tuteur = result.scalar_one_or_none()
    if tuteur is None:
        raise HTTPException(status_code=404, detail="Tuteur introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tuteur, field, value)
    await db.flush()
    return await get_eleve(db, eleve_id)


async def delete_tuteur(db: AsyncSession, eleve_id: UUID, tuteur_id: UUID) -> Eleve:
    result = await db.execute(
        select(Tuteur).where(Tuteur.id == tuteur_id, Tuteur.eleve_id == eleve_id)
    )
    tuteur = result.scalar_one_or_none()
    if tuteur is None:
        raise HTTPException(status_code=404, detail="Tuteur introuvable")
    await db.delete(tuteur)
    await db.flush()
    return await get_eleve(db, eleve_id)


async def affecter_classe(db: AsyncSession, eleve_id: UUID, classe_id: UUID) -> Eleve:
    eleve = await get_eleve(db, eleve_id)
    if eleve.statut != StatutEleve.ACTIF.value:
        raise HTTPException(status_code=400, detail="Élève inactif")

    annee = await parametrage_service.get_annee_active(db)
    if annee is None:
        raise HTTPException(status_code=400, detail="Aucune année scolaire active")

    inscription = _get_inscription_for_annee(eleve, annee.id)
    if inscription is None:
        raise HTTPException(status_code=400, detail="Aucune inscription pour l'année active")

    classe = await classe_service.verify_capacity(db, classe_id, annee.id)
    if classe.niveau_id != inscription.niveau_id:
        raise HTTPException(
            status_code=400,
            detail="La classe ne correspond pas au niveau de l'élève",
        )

    if inscription.classe_id and inscription.classe_id != classe_id:
        pass  # changement de classe autorisé si capacité OK

    inscription.classe_id = classe_id
    await db.flush()
    return await get_eleve(db, eleve_id)


async def create_transfert_entrant(db: AsyncSession, data: TransfertEntrantCreate) -> Eleve:
    eleve = await create_eleve(db, data)
    db.add(
        Transfert(
            eleve_id=eleve.id,
            type=TypeTransfert.ENTRANT.value,
            ecole=data.ecole_origine,
            date_transfert=data.date_transfert or date.today(),
            observations=data.observations,
        )
    )
    await db.flush()
    return await get_eleve(db, eleve.id)


async def transfert_sortant(
    db: AsyncSession,
    eleve_id: UUID,
    data: TransfertSortantRequest,
) -> Eleve:
    eleve = await get_eleve(db, eleve_id)
    if eleve.statut != StatutEleve.ACTIF.value:
        raise HTTPException(status_code=400, detail="Élève déjà inactif")

    annee = await parametrage_service.get_annee_active(db)
    if annee:
        inscription = _get_inscription_for_annee(eleve, annee.id)
        if inscription:
            inscription.statut = StatutEleve.INACTIF.value
            inscription.classe_id = None

    eleve.statut = StatutEleve.INACTIF.value
    eleve.motif_inactivite = data.motif or "Transfert sortant"
    eleve.date_inactivite = data.date_transfert or date.today()

    db.add(
        Transfert(
            eleve_id=eleve.id,
            type=TypeTransfert.SORTANT.value,
            ecole=data.ecole_destination,
            date_transfert=data.date_transfert or date.today(),
            motif=data.motif,
        )
    )
    await db.flush()
    return await get_eleve(db, eleve.id)


async def desactiver_eleve(
    db: AsyncSession,
    eleve_id: UUID,
    motif: str,
    date_inactivite: date | None = None,
) -> Eleve:
    eleve = await get_eleve(db, eleve_id)
    eleve.statut = StatutEleve.INACTIF.value
    eleve.motif_inactivite = motif
    eleve.date_inactivite = date_inactivite or date.today()

    annee = await parametrage_service.get_annee_active(db)
    if annee:
        inscription = _get_inscription_for_annee(eleve, annee.id)
        if inscription:
            inscription.statut = StatutEleve.INACTIF.value
            inscription.classe_id = None

    await db.flush()
    return await get_eleve(db, eleve_id)


async def get_historique(db: AsyncSession, eleve_id: UUID) -> HistoriqueScolaireResponse:
    eleve = await get_eleve(db, eleve_id)
    return HistoriqueScolaireResponse(
        eleve_id=eleve.id,
        matricule=eleve.matricule,
        nom=eleve.nom,
        prenoms=eleve.prenoms,
        inscriptions=sorted(eleve.inscriptions, key=lambda i: i.date_inscription, reverse=True),
        transferts=sorted(eleve.transferts, key=lambda t: t.date_transfert, reverse=True),
    )


async def get_stats_effectifs(db: AsyncSession) -> EffectifStatsResponse:
    annee = await parametrage_service.get_annee_active(db)
    if annee is None:
        return EffectifStatsResponse(
            total_eleves=0, total_garcons=0, total_filles=0, par_niveau=[], sans_classe=0
        )

    result = await db.execute(
        select(Eleve, Inscription, Niveau)
        .join(Inscription, Inscription.eleve_id == Eleve.id)
        .join(Niveau, Niveau.id == Inscription.niveau_id)
        .where(
            Inscription.annee_scolaire_id == annee.id,
            Eleve.statut == StatutEleve.ACTIF.value,
            Inscription.statut == StatutEleve.ACTIF.value,
        )
    )
    rows = result.all()

    par_niveau: dict[str, EffectifNiveauStat] = {}
    sans_classe = 0
    total_g = total_f = 0

    for eleve, inscription, niveau in rows:
        total_g += 1 if eleve.sexe == "M" else 0
        total_f += 1 if eleve.sexe == "F" else 0
        if not inscription.classe_id:
            sans_classe += 1

        if niveau.code not in par_niveau:
            par_niveau[niveau.code] = EffectifNiveauStat(
                niveau_code=niveau.code,
                niveau_libelle=niveau.libelle,
                total=0,
                garcons=0,
                filles=0,
            )
        stat = par_niveau[niveau.code]
        stat.total += 1
        if eleve.sexe == "M":
            stat.garcons += 1
        else:
            stat.filles += 1

    return EffectifStatsResponse(
        total_eleves=len(rows),
        total_garcons=total_g,
        total_filles=total_f,
        par_niveau=sorted(par_niveau.values(), key=lambda x: x.niveau_code),
        sans_classe=sans_classe,
    )
