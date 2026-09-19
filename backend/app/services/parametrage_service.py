from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.parametrage import (
    AnneeScolaire,
    Bareme,
    CalendrierScolaire,
    Classe,
    Etablissement,
    Matiere,
    Niveau,
    Periode,
    Referentiel,
    StatutAnneeScolaire,
    TypeFrais,
    matiere_niveaux,
)
from app.schemas.parametrage import (
    AnneeScolaireCreate,
    AnneeScolaireUpdate,
    BaremeUpdate,
    CalendrierCreate,
    CalendrierUpdate,
    ClasseCreate,
    ClasseUpdate,
    EtablissementUpdate,
    MatiereCreate,
    MatiereUpdate,
    NiveauCreate,
    NiveauUpdate,
    ParametrageStatutResponse,
    PeriodeCreate,
    PeriodeUpdate,
    TypeFraisCreate,
    TypeFraisUpdate,
)


async def get_etablissement(db: AsyncSession) -> Etablissement | None:
    result = await db.execute(select(Etablissement).limit(1))
    return result.scalar_one_or_none()


async def update_etablissement(db: AsyncSession, data: EtablissementUpdate) -> Etablissement:
    etab = await get_etablissement(db)
    if etab is None:
        raise HTTPException(status_code=404, detail="Établissement non configuré")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(etab, field, value)
    await db.flush()
    await db.refresh(etab)
    return etab


async def list_annees(db: AsyncSession) -> list[AnneeScolaire]:
    result = await db.execute(select(AnneeScolaire).order_by(AnneeScolaire.date_debut.desc()))
    return list(result.scalars().all())


async def get_annee_active(db: AsyncSession) -> AnneeScolaire | None:
    result = await db.execute(select(AnneeScolaire).where(AnneeScolaire.is_active.is_(True)))
    return result.scalar_one_or_none()


async def create_annee(db: AsyncSession, data: AnneeScolaireCreate) -> AnneeScolaire:
    annee = AnneeScolaire(
        libelle=data.libelle,
        date_debut=data.date_debut,
        date_fin=data.date_fin,
        statut=StatutAnneeScolaire.PLANIFIEE.value,
    )
    db.add(annee)
    await db.flush()

    bareme = Bareme(annee_scolaire_id=annee.id)
    db.add(bareme)
    await db.flush()
    return annee


async def update_annee(db: AsyncSession, annee_id: UUID, data: AnneeScolaireUpdate) -> AnneeScolaire:
    annee = await _get_annee(db, annee_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(annee, field, value)
    await db.flush()
    return annee


async def activer_annee(db: AsyncSession, annee_id: UUID) -> AnneeScolaire:
    annee = await _get_annee(db, annee_id)
    if annee.statut == StatutAnneeScolaire.CLOTUREE.value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Année clôturée — réouverture impossible sans intervention admin",
        )
    await db.execute(sql_update(AnneeScolaire).values(is_active=False))
    annee.is_active = True
    annee.statut = StatutAnneeScolaire.ACTIVE.value
    await db.flush()
    return annee


async def cloturer_annee(db: AsyncSession, annee_id: UUID) -> AnneeScolaire:
    annee = await _get_annee(db, annee_id)
    if annee.is_active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Désactivez l'année avant de la clôturer",
        )
    if annee.statut == StatutAnneeScolaire.CLOTUREE.value:
        raise HTTPException(status_code=422, detail="Année déjà clôturée")
    annee.statut = StatutAnneeScolaire.CLOTUREE.value
    annee.is_active = False
    await db.flush()
    return annee


async def ensure_annee_modifiable(db: AsyncSession, annee_id: UUID) -> None:
    annee = await _get_annee(db, annee_id)
    if annee.statut == StatutAnneeScolaire.CLOTUREE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Année scolaire clôturée — modification impossible (lecture seule)",
        )


async def _get_annee(db: AsyncSession, annee_id: UUID) -> AnneeScolaire:
    result = await db.execute(select(AnneeScolaire).where(AnneeScolaire.id == annee_id))
    annee = result.scalar_one_or_none()
    if annee is None:
        raise HTTPException(status_code=404, detail="Année scolaire introuvable")
    return annee


async def list_niveaux(db: AsyncSession) -> list[Niveau]:
    result = await db.execute(select(Niveau).order_by(Niveau.ordre))
    return list(result.scalars().all())


async def create_niveau(db: AsyncSession, data: NiveauCreate) -> Niveau:
    niveau = Niveau(**data.model_dump())
    db.add(niveau)
    await db.flush()
    return niveau


async def update_niveau(db: AsyncSession, niveau_id: UUID, data: NiveauUpdate) -> Niveau:
    niveau = await _get_niveau(db, niveau_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(niveau, field, value)
    await db.flush()
    return niveau


async def _get_niveau(db: AsyncSession, niveau_id: UUID) -> Niveau:
    result = await db.execute(select(Niveau).where(Niveau.id == niveau_id))
    niveau = result.scalar_one_or_none()
    if niveau is None:
        raise HTTPException(status_code=404, detail="Niveau introuvable")
    return niveau


async def list_classes(db: AsyncSession, annee_id: UUID | None = None) -> list[Classe]:
    query = select(Classe).options(selectinload(Classe.niveau))
    if annee_id:
        query = query.where(Classe.annee_scolaire_id == annee_id)
    result = await db.execute(query.order_by(Classe.nom))
    return list(result.scalars().all())


async def create_classe(db: AsyncSession, data: ClasseCreate) -> Classe:
    await _get_niveau(db, data.niveau_id)
    await _get_annee(db, data.annee_scolaire_id)
    classe = Classe(**data.model_dump())
    db.add(classe)
    await db.flush()
    return await get_classe(db, classe.id)


async def update_classe(db: AsyncSession, classe_id: UUID, data: ClasseUpdate) -> Classe:
    classe = await get_classe(db, classe_id)
    if data.niveau_id:
        await _get_niveau(db, data.niveau_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(classe, field, value)
    await db.flush()
    return await get_classe(db, classe_id)


async def get_classe(db: AsyncSession, classe_id: UUID) -> Classe:
    result = await db.execute(
        select(Classe).options(selectinload(Classe.niveau)).where(Classe.id == classe_id)
    )
    classe = result.scalar_one_or_none()
    if classe is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")
    return classe


async def list_matieres(db: AsyncSession) -> list[Matiere]:
    result = await db.execute(
        select(Matiere).options(selectinload(Matiere.niveaux)).order_by(Matiere.libelle)
    )
    return list(result.scalars().all())


async def create_matiere(db: AsyncSession, data: MatiereCreate) -> Matiere:
    matiere = Matiere(
        code=data.code,
        libelle=data.libelle,
        coefficient_defaut=data.coefficient_defaut,
    )
    if data.niveaux:
        niveau_ids = [n.niveau_id for n in data.niveaux]
        niveaux = await _get_niveaux_by_ids(db, niveau_ids)
        matiere.niveaux = niveaux
        db.add(matiere)
        await db.flush()
        await _set_matiere_coefficients(db, matiere.id, data.niveaux)
    else:
        db.add(matiere)
        await db.flush()
    return await get_matiere(db, matiere.id)


async def update_matiere(db: AsyncSession, matiere_id: UUID, data: MatiereUpdate) -> Matiere:
    matiere = await get_matiere(db, matiere_id)
    if data.libelle is not None:
        matiere.libelle = data.libelle
    if data.coefficient_defaut is not None:
        matiere.coefficient_defaut = data.coefficient_defaut
    if data.niveaux is not None:
        niveau_ids = [n.niveau_id for n in data.niveaux]
        matiere.niveaux = await _get_niveaux_by_ids(db, niveau_ids)
        await db.flush()
        await _set_matiere_coefficients(db, matiere.id, data.niveaux)
    await db.flush()
    return await get_matiere(db, matiere_id)


async def get_matiere(db: AsyncSession, matiere_id: UUID) -> Matiere:
    result = await db.execute(
        select(Matiere).options(selectinload(Matiere.niveaux)).where(Matiere.id == matiere_id)
    )
    matiere = result.scalar_one_or_none()
    if matiere is None:
        raise HTTPException(status_code=404, detail="Matière introuvable")
    return matiere


async def _get_niveaux_by_ids(db: AsyncSession, ids: list[UUID]) -> list[Niveau]:
    result = await db.execute(select(Niveau).where(Niveau.id.in_(ids)))
    niveaux = list(result.scalars().all())
    if len(niveaux) != len(set(ids)):
        raise HTTPException(status_code=400, detail="Niveau invalide")
    return niveaux


async def _set_matiere_coefficients(db: AsyncSession, matiere_id: UUID, niveaux_data) -> None:
    for item in niveaux_data:
        await db.execute(
            sql_update(matiere_niveaux)
            .where(
                matiere_niveaux.c.matiere_id == matiere_id,
                matiere_niveaux.c.niveau_id == item.niveau_id,
            )
            .values(coefficient=item.coefficient)
        )


async def list_periodes(db: AsyncSession, annee_id: UUID) -> list[Periode]:
    result = await db.execute(
        select(Periode)
        .where(Periode.annee_scolaire_id == annee_id)
        .order_by(Periode.ordre)
    )
    return list(result.scalars().all())


async def create_periode(db: AsyncSession, data: PeriodeCreate) -> Periode:
    await _get_annee(db, data.annee_scolaire_id)
    periode = Periode(**data.model_dump())
    db.add(periode)
    await db.flush()
    return periode


async def update_periode(db: AsyncSession, periode_id: UUID, data: PeriodeUpdate) -> Periode:
    result = await db.execute(select(Periode).where(Periode.id == periode_id))
    periode = result.scalar_one_or_none()
    if periode is None:
        raise HTTPException(status_code=404, detail="Période introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(periode, field, value)
    await db.flush()
    return periode


async def get_bareme(db: AsyncSession, annee_id: UUID) -> Bareme:
    result = await db.execute(select(Bareme).where(Bareme.annee_scolaire_id == annee_id))
    bareme = result.scalar_one_or_none()
    if bareme is None:
        raise HTTPException(status_code=404, detail="Barème introuvable")
    return bareme


async def update_bareme(db: AsyncSession, annee_id: UUID, data: BaremeUpdate) -> Bareme:
    bareme = await get_bareme(db, annee_id)
    for field, value in data.model_dump().items():
        setattr(bareme, field, value)
    await db.flush()
    return bareme


async def list_types_frais(db: AsyncSession) -> list[TypeFrais]:
    result = await db.execute(select(TypeFrais).order_by(TypeFrais.libelle))
    return list(result.scalars().all())


async def create_type_frais(db: AsyncSession, data: TypeFraisCreate) -> TypeFrais:
    type_frais = TypeFrais(**data.model_dump())
    db.add(type_frais)
    await db.flush()
    return type_frais


async def update_type_frais(db: AsyncSession, type_id: UUID, data: TypeFraisUpdate) -> TypeFrais:
    result = await db.execute(select(TypeFrais).where(TypeFrais.id == type_id))
    type_frais = result.scalar_one_or_none()
    if type_frais is None:
        raise HTTPException(status_code=404, detail="Type de frais introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(type_frais, field, value)
    await db.flush()
    return type_frais


async def list_calendrier(db: AsyncSession, annee_id: UUID) -> list[CalendrierScolaire]:
    result = await db.execute(
        select(CalendrierScolaire)
        .where(CalendrierScolaire.annee_scolaire_id == annee_id)
        .order_by(CalendrierScolaire.date_debut)
    )
    return list(result.scalars().all())


async def create_calendrier(db: AsyncSession, data: CalendrierCreate) -> CalendrierScolaire:
    await _get_annee(db, data.annee_scolaire_id)
    entry = CalendrierScolaire(**data.model_dump())
    db.add(entry)
    await db.flush()
    return entry


async def update_calendrier(
    db: AsyncSession, entry_id: UUID, data: CalendrierUpdate
) -> CalendrierScolaire:
    result = await db.execute(select(CalendrierScolaire).where(CalendrierScolaire.id == entry_id))
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Entrée calendrier introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await db.flush()
    return entry


async def list_referentiels(db: AsyncSession, ref_type: str) -> list[Referentiel]:
    result = await db.execute(
        select(Referentiel).where(Referentiel.type == ref_type).order_by(Referentiel.libelle)
    )
    return list(result.scalars().all())


async def get_parametrage_statut(db: AsyncSession) -> ParametrageStatutResponse:
    etab = await get_etablissement(db)
    annee = await get_annee_active(db)

    niveaux_count = (await db.execute(select(func.count()).select_from(Niveau))).scalar_one()
    classes_count = (await db.execute(select(func.count()).select_from(Classe))).scalar_one()
    matieres_count = (await db.execute(select(func.count()).select_from(Matiere))).scalar_one()
    types_frais_count = (await db.execute(select(func.count()).select_from(TypeFrais))).scalar_one()

    periodes_count = 0
    if annee:
        periodes_count = (
            await db.execute(
                select(func.count()).select_from(Periode).where(Periode.annee_scolaire_id == annee.id)
            )
        ).scalar_one()

    pret = bool(
        etab
        and annee
        and niveaux_count > 0
        and classes_count > 0
        and matieres_count > 0
        and periodes_count > 0
        and types_frais_count > 0
    )

    return ParametrageStatutResponse(
        etablissement_configure=etab is not None,
        annee_active=annee is not None,
        niveaux_count=niveaux_count,
        classes_count=classes_count,
        matieres_count=matieres_count,
        periodes_count=periodes_count,
        types_frais_count=types_frais_count,
        pret_pour_inscriptions=pret,
    )
