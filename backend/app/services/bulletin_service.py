from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bulletins import Competence, DecisionPassage, EvaluationCompetence
from app.models.eleve import Eleve, Inscription
from app.models.parametrage import AnneeScolaire, Classe, Niveau, Periode, TypeNiveau
from app.schemas.bulletins import (
    BulletinEleveData,
    CompetenceBulkUpdate,
    CompetenceGrilleResponse,
    CompetenceGrilleRow,
    CompetenceResponse,
    DecisionPassageCreate,
    DecisionPassageResponse,
    PalmaresItem,
    PalmaresResponse,
    StatsPedagogiquesResponse,
)
from app.services import classe_service, notes_service, parametrage_service, pdf_service


async def _get_eleve_classe(db: AsyncSession, eleve_id: UUID) -> tuple[Eleve, Classe]:
    eleve = await db.get(Eleve, eleve_id)
    if eleve is None:
        raise HTTPException(status_code=404, detail="Élève introuvable")
    classe_result = await db.execute(
        select(Classe)
        .join(Inscription, Inscription.classe_id == Classe.id)
        .where(Inscription.eleve_id == eleve_id)
        .limit(1)
    )
    classe = classe_result.scalar_one_or_none()
    if classe is None:
        raise HTTPException(status_code=404, detail="Classe introuvable pour cet élève")
    return eleve, classe


async def _get_decision(
    db: AsyncSession, eleve_id: UUID, annee_id: UUID
) -> DecisionPassage | None:
    result = await db.execute(
        select(DecisionPassage).where(
            DecisionPassage.eleve_id == eleve_id,
            DecisionPassage.annee_scolaire_id == annee_id,
        )
    )
    return result.scalar_one_or_none()


async def get_bulletin_data(
    db: AsyncSession,
    eleve_id: UUID,
    periode_id: UUID,
) -> BulletinEleveData:
    eleve, classe = await _get_eleve_classe(db, eleve_id)
    periode = await db.get(Periode, periode_id)
    if periode is None:
        raise HTTPException(status_code=404, detail="Période introuvable")

    moyennes = await notes_service.get_moyennes_classe(db, classe.id, periode_id)
    eleve_moy = next((e for e in moyennes.eleves if e.eleve_id == eleve_id), None)
    if eleve_moy is None:
        raise HTTPException(status_code=404, detail="Données de notes introuvables")

    annee = await db.get(AnneeScolaire, classe.annee_scolaire_id)
    decision = await _get_decision(db, eleve_id, classe.annee_scolaire_id)

    return BulletinEleveData(
        eleve_id=eleve.id,
        matricule=eleve.matricule,
        nom=eleve.nom,
        prenoms=eleve.prenoms,
        classe_nom=classe.nom,
        periode_libelle=periode.libelle,
        annee_libelle=annee.libelle if annee else "—",
        moyennes=eleve_moy,
        decision=decision.decision if decision else None,
        observation=decision.observation if decision else None,
    )


async def generate_bulletin_pdf(
    db: AsyncSession,
    eleve_id: UUID,
    periode_id: UUID,
) -> bytes:
    data = await get_bulletin_data(db, eleve_id, periode_id)
    etab = await parametrage_service.get_etablissement(db)
    return pdf_service.generate_bulletin_primaire(data, etab)


async def generate_bulletins_classe_pdf(
    db: AsyncSession,
    classe_id: UUID,
    periode_id: UUID,
) -> bytes:
    eleves = await classe_service.list_eleves_classe(db, classe_id)
    etab = await parametrage_service.get_etablissement(db)
    bulletins: list[BulletinEleveData] = []
    for e in eleves.eleves:
        try:
            bulletins.append(await get_bulletin_data(db, e.id, periode_id))
        except HTTPException:
            continue
    return pdf_service.generate_bulletins_classe(bulletins, etab)


async def generate_bulletin_annuel_pdf(db: AsyncSession, eleve_id: UUID) -> bytes:
    eleve, classe = await _get_eleve_classe(db, eleve_id)
    periodes = await db.execute(
        select(Periode).where(Periode.annee_scolaire_id == classe.annee_scolaire_id).order_by(Periode.ordre)
    )
    trimestres = list(periodes.scalars().all())

    moyennes_trim: list[tuple[str, Decimal | None]] = []
    for p in trimestres:
        try:
            m = await notes_service.get_moyennes_classe(db, classe.id, p.id)
            em = next((e for e in m.eleves if e.eleve_id == eleve_id), None)
            moyennes_trim.append((p.libelle, em.moyenne_generale if em else None))
        except HTTPException:
            moyennes_trim.append((p.libelle, None))

    vals = [v for _, v in moyennes_trim if v is not None]
    moy_annuelle = sum(vals) / len(vals) if vals else None
    if moy_annuelle is not None:
        bareme = await parametrage_service.get_bareme(db, classe.annee_scolaire_id)
        q = Decimal("0.1") ** bareme.arrondi_decimales
        moy_annuelle = moy_annuelle.quantize(q, rounding=ROUND_HALF_UP)

    annee = await db.get(AnneeScolaire, classe.annee_scolaire_id)
    decision = await _get_decision(db, eleve_id, classe.annee_scolaire_id)
    etab = await parametrage_service.get_etablissement(db)

    return pdf_service.generate_bulletin_annuel(
        eleve, classe.nom, annee.libelle if annee else "—",
        moyennes_trim, moy_annuelle,
        decision.decision if decision else None,
        etab,
    )


async def get_stats_pedagogiques(
    db: AsyncSession,
    classe_id: UUID,
    periode_id: UUID,
) -> StatsPedagogiquesResponse:
    classe = await db.get(Classe, classe_id)
    if classe is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    moyennes = await notes_service.get_moyennes_classe(db, classe_id, periode_id)
    bareme = await parametrage_service.get_bareme(db, classe.annee_scolaire_id)

    with_moy = [e for e in moyennes.eleves if e.moyenne_generale is not None]
    if not with_moy:
        return StatsPedagogiquesResponse(
            classe_id=classe_id,
            classe_nom=classe.nom,
            periode_libelle=moyennes.periode_libelle,
            effectif=len(moyennes.eleves),
            moyenne_classe=None,
            taux_reussite=None,
            meilleur_eleve=None,
            moins_bonne_moyenne=None,
        )

    total = sum(e.moyenne_generale for e in with_moy if e.moyenne_generale)
    moy_classe = total / len(with_moy)
    reussis = sum(1 for e in with_moy if e.moyenne_generale and e.moyenne_generale >= bareme.seuil_passage)
    best = max(with_moy, key=lambda x: x.moyenne_generale or Decimal("0"))

    return StatsPedagogiquesResponse(
        classe_id=classe_id,
        classe_nom=classe.nom,
        periode_libelle=moyennes.periode_libelle,
        effectif=len(moyennes.eleves),
        moyenne_classe=moy_classe.quantize(Decimal("0.01")),
        taux_reussite=Decimal(reussis / len(with_moy) * 100).quantize(Decimal("0.1")),
        meilleur_eleve=f"{best.prenoms} {best.nom}",
        moins_bonne_moyenne=min(e.moyenne_generale for e in with_moy if e.moyenne_generale),
    )


async def get_palmares(
    db: AsyncSession,
    classe_id: UUID,
    periode_id: UUID,
    limit: int = 10,
) -> PalmaresResponse:
    moyennes = await notes_service.get_moyennes_classe(db, classe_id, periode_id)
    ranked = sorted(
        [e for e in moyennes.eleves if e.moyenne_generale is not None and e.rang is not None],
        key=lambda x: x.rang or 999,
    )[:limit]

    return PalmaresResponse(
        classe_id=classe_id,
        classe_nom=moyennes.classe_nom,
        periode_libelle=moyennes.periode_libelle,
        items=[
            PalmaresItem(
                rang=e.rang or 0,
                eleve_id=e.eleve_id,
                nom=e.nom,
                prenoms=e.prenoms,
                matricule=e.matricule,
                moyenne_generale=e.moyenne_generale or Decimal("0"),
                appreciation=e.appreciation_generale,
            )
            for e in ranked
        ],
    )


async def set_decision_passage(
    db: AsyncSession,
    data: DecisionPassageCreate,
) -> DecisionPassageResponse:
    annee = await parametrage_service.get_annee_active(db)
    if annee is None:
        raise HTTPException(status_code=422, detail="Aucune année active")
    annee_id = data.annee_scolaire_id or annee.id

    result = await db.execute(
        select(DecisionPassage).where(
            DecisionPassage.eleve_id == data.eleve_id,
            DecisionPassage.annee_scolaire_id == annee_id,
        )
    )
    decision = result.scalar_one_or_none()
    if decision is None:
        decision = DecisionPassage(
            eleve_id=data.eleve_id,
            annee_scolaire_id=annee_id,
            decision=data.decision,
            observation=data.observation,
        )
        db.add(decision)
    else:
        decision.decision = data.decision
        decision.observation = data.observation

    await db.commit()
    await db.refresh(decision)
    return DecisionPassageResponse.model_validate(decision)


async def list_competences(db: AsyncSession, niveau_id: UUID) -> list[Competence]:
    result = await db.execute(
        select(Competence).where(Competence.niveau_id == niveau_id).order_by(Competence.domaine, Competence.ordre)
    )
    return list(result.scalars().all())


async def get_grille_competences(
    db: AsyncSession,
    classe_id: UUID,
    periode_id: UUID,
) -> CompetenceGrilleResponse:
    classe = await db.execute(
        select(Classe).options(selectinload(Classe.niveau)).where(Classe.id == classe_id)
    )
    c = classe.scalar_one_or_none()
    if c is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    if c.niveau.type != TypeNiveau.MATERNELLE.value:
        raise HTTPException(status_code=422, detail="Cette classe n'est pas de maternelle")

    periode = await db.get(Periode, periode_id)
    competences = await list_competences(db, c.niveau_id)
    eleves = await classe_service.list_eleves_classe(db, classe_id)

    evals_result = await db.execute(
        select(EvaluationCompetence).where(
            EvaluationCompetence.periode_id == periode_id,
            EvaluationCompetence.eleve_id.in_([e.id for e in eleves.eleves]),
        )
    )
    eval_map: dict[tuple, EvaluationCompetence] = {
        (ev.eleve_id, ev.competence_id): ev for ev in evals_result.scalars().all()
    }

    rows: list[CompetenceGrilleRow] = []
    for e in eleves.eleves:
        ev_dict = {
            str(comp.id): eval_map.get((e.id, comp.id)).statut if (e.id, comp.id) in eval_map else None
            for comp in competences
        }
        rows.append(
            CompetenceGrilleRow(
                eleve_id=e.id,
                matricule=e.matricule,
                nom=e.nom,
                prenoms=e.prenoms,
                evaluations=ev_dict,
            )
        )

    return CompetenceGrilleResponse(
        classe_id=classe_id,
        classe_nom=c.nom,
        periode_libelle=periode.libelle if periode else "—",
        competences=[CompetenceResponse.model_validate(comp) for comp in competences],
        eleves=rows,
    )


async def bulk_update_competences(
    db: AsyncSession,
    periode_id: UUID,
    items: list[CompetenceBulkUpdate],
) -> CompetenceGrilleResponse:
    classe_id: UUID | None = None
    for item in items:
        for ev in item.evaluations:
            result = await db.execute(
                select(EvaluationCompetence).where(
                    EvaluationCompetence.eleve_id == item.eleve_id,
                    EvaluationCompetence.competence_id == ev.competence_id,
                    EvaluationCompetence.periode_id == periode_id,
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                existing.statut = ev.statut
                existing.appreciation = ev.appreciation
            else:
                db.add(
                    EvaluationCompetence(
                        eleve_id=item.eleve_id,
                        competence_id=ev.competence_id,
                        periode_id=periode_id,
                        statut=ev.statut,
                        appreciation=ev.appreciation,
                    )
                )
        if classe_id is None:
            _, classe = await _get_eleve_classe(db, item.eleve_id)
            classe_id = classe.id

    await db.commit()
    if classe_id is None:
        raise HTTPException(status_code=422, detail="Aucune donnée")
    return await get_grille_competences(db, classe_id, periode_id)


async def generate_bulletin_maternelle_pdf(
    db: AsyncSession,
    eleve_id: UUID,
    periode_id: UUID,
) -> bytes:
    eleve, classe = await _get_eleve_classe(db, eleve_id)
    grille = await get_grille_competences(db, classe.id, periode_id)
    row = next((r for r in grille.eleves if r.eleve_id == eleve_id), None)
    if row is None:
        raise HTTPException(status_code=404, detail="Élève introuvable")

    etab = await parametrage_service.get_etablissement(db)
    return pdf_service.generate_bulletin_maternelle(eleve, grille, row, etab)
