from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.eleve import Eleve, Inscription, StatutEleve
from app.models.notes import Evaluation, Note, TypeEvaluation, ValidationPeriode
from app.models.parametrage import Bareme, Classe, Matiere, Periode, matiere_niveaux
from app.schemas.notes import (
    EleveMoyennesItem,
    EleveNoteRow,
    EvaluationCreate,
    EvaluationResponse,
    GrilleNotesResponse,
    MoyenneMatiereItem,
    MoyennesClasseResponse,
    NoteItem,
    NoteResponse,
    NotesBulkUpdate,
    TypeEvaluationCreate,
    TypeEvaluationResponse,
    ValidationResponse,
)
from app.models.audit import HistoriqueNote
from app.services import audit_service, classe_service, parametrage_service


def _bareme_max(echelle: str) -> Decimal:
    if echelle == "/10":
        return Decimal("10")
    if echelle == "/100":
        return Decimal("100")
    return Decimal("20")


def _auto_appreciation(moyenne: Decimal, bareme: Bareme) -> str:
    max_n = _bareme_max(bareme.echelle)
    ratio = moyenne / max_n * Decimal("20")
    if ratio >= Decimal("16"):
        return "Excellent"
    if ratio >= Decimal("14"):
        return "Très bien"
    if ratio >= Decimal("12"):
        return "Bien"
    if ratio >= Decimal("10"):
        return "Assez bien"
    if ratio >= bareme.seuil_redoublement:
        return "Passable"
    return "Insuffisant"


def _round_note(val: Decimal, bareme: Bareme) -> Decimal:
    q = Decimal("0.1") ** bareme.arrondi_decimales
    return val.quantize(q, rounding=ROUND_HALF_UP)


async def _get_bareme(db: AsyncSession, annee_id: UUID) -> Bareme:
    return await parametrage_service.get_bareme(db, annee_id)


async def _is_verrouille(db: AsyncSession, classe_id: UUID, periode_id: UUID) -> bool:
    result = await db.execute(
        select(ValidationPeriode).where(
            ValidationPeriode.classe_id == classe_id,
            ValidationPeriode.periode_id == periode_id,
        )
    )
    v = result.scalar_one_or_none()
    return v.verrouille if v else False


async def _ensure_not_verrouille(db: AsyncSession, classe_id: UUID, periode_id: UUID) -> None:
    if await _is_verrouille(db, classe_id, periode_id):
        raise HTTPException(status_code=403, detail="Notes verrouillées pour cette période")


def _validate_valeur(valeur: Decimal | None, is_absent: bool, bareme: Bareme) -> None:
    if is_absent:
        return
    if valeur is None:
        raise HTTPException(status_code=422, detail="Valeur requise sauf pour ABS")
    max_n = _bareme_max(bareme.echelle)
    if valeur < 0 or valeur > max_n:
        raise HTTPException(status_code=422, detail=f"Note hors barème (0-{max_n})")


async def list_types_evaluation(
    db: AsyncSession,
    annee_id: UUID | None = None,
) -> list[TypeEvaluation]:
    if annee_id is None:
        annee = await parametrage_service.get_annee_active(db)
        if annee is None:
            return []
        annee_id = annee.id
    result = await db.execute(
        select(TypeEvaluation).where(TypeEvaluation.annee_scolaire_id == annee_id)
    )
    return list(result.scalars().all())


async def create_type_evaluation(db: AsyncSession, data: TypeEvaluationCreate) -> TypeEvaluation:
    annee = await parametrage_service.get_annee_active(db)
    if annee is None:
        raise HTTPException(status_code=422, detail="Aucune année active")
    annee_id = data.annee_scolaire_id or annee.id
    te = TypeEvaluation(annee_scolaire_id=annee_id, **data.model_dump(exclude={"annee_scolaire_id"}))
    db.add(te)
    await db.commit()
    await db.refresh(te)
    return te


async def create_evaluation(db: AsyncSession, data: EvaluationCreate) -> Evaluation:
    classe = await db.get(Classe, data.classe_id)
    if classe is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")
    await _ensure_not_verrouille(db, data.classe_id, data.periode_id)

    type_eval = await db.get(TypeEvaluation, data.type_evaluation_id)
    if type_eval is None:
        raise HTTPException(status_code=404, detail="Type d'évaluation introuvable")

    coef = data.coefficient if data.coefficient is not None else type_eval.coefficient_defaut
    ev = Evaluation(
        annee_scolaire_id=classe.annee_scolaire_id,
        coefficient=coef,
        **data.model_dump(exclude={"coefficient"}),
    )
    db.add(ev)
    await db.commit()
    result = await db.execute(
        select(Evaluation)
        .options(selectinload(Evaluation.type_evaluation))
        .where(Evaluation.id == ev.id)
    )
    return result.scalar_one()


async def get_grille_notes(db: AsyncSession, evaluation_id: UUID) -> GrilleNotesResponse:
    result = await db.execute(
        select(Evaluation)
        .options(selectinload(Evaluation.type_evaluation), selectinload(Evaluation.notes))
        .where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Évaluation introuvable")

    bareme = await _get_bareme(db, evaluation.annee_scolaire_id)
    verrouille = await _is_verrouille(db, evaluation.classe_id, evaluation.periode_id)
    eleves_data = await classe_service.list_eleves_classe(db, evaluation.classe_id)
    notes_map = {n.eleve_id: n for n in evaluation.notes}

    rows = [
        EleveNoteRow(
            eleve_id=e.id,
            matricule=e.matricule,
            nom=e.nom,
            prenoms=e.prenoms,
            note=NoteResponse.model_validate(notes_map[e.id]) if e.id in notes_map else None,
        )
        for e in eleves_data.eleves
    ]

    return GrilleNotesResponse(
        evaluation=EvaluationResponse.model_validate(evaluation),
        verrouille=verrouille,
        eleves=rows,
        bareme_max=_bareme_max(bareme.echelle),
        echelle=bareme.echelle,
    )


async def bulk_update_notes(
    db: AsyncSession,
    evaluation_id: UUID,
    data: NotesBulkUpdate,
    user_id: UUID | None = None,
    ip_address: str | None = None,
    user_email: str | None = None,
) -> GrilleNotesResponse:
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Évaluation introuvable")

    await parametrage_service.ensure_annee_modifiable(db, evaluation.annee_scolaire_id)
    await _ensure_not_verrouille(db, evaluation.classe_id, evaluation.periode_id)
    bareme = await _get_bareme(db, evaluation.annee_scolaire_id)

    existing = await db.execute(select(Note).where(Note.evaluation_id == evaluation_id))
    notes_map = {n.eleve_id: n for n in existing.scalars().all()}
    changes = 0

    for item in data.notes:
        _validate_valeur(item.valeur, item.is_absent, bareme)
        auto = None
        if not item.is_absent and item.valeur is not None:
            auto = _auto_appreciation(item.valeur, bareme)

        new_valeur = None if item.is_absent else item.valeur
        if item.eleve_id in notes_map:
            note = notes_map[item.eleve_id]
            if note.valeur != new_valeur or note.is_absent != item.is_absent:
                db.add(
                    HistoriqueNote(
                        note_id=note.id,
                        evaluation_id=evaluation_id,
                        eleve_id=item.eleve_id,
                        annee_scolaire_id=evaluation.annee_scolaire_id,
                        ancienne_valeur=note.valeur,
                        nouvelle_valeur=new_valeur,
                        ancien_absent=note.is_absent,
                        nouveau_absent=item.is_absent,
                        modifie_par_id=user_id,
                        ip_address=ip_address,
                    )
                )
                changes += 1
            note.valeur = new_valeur
            note.is_absent = item.is_absent
            note.appreciation_libre = item.appreciation_libre
            note.appreciation_auto = auto
        else:
            db.add(
                Note(
                    evaluation_id=evaluation_id,
                    eleve_id=item.eleve_id,
                    valeur=new_valeur,
                    is_absent=item.is_absent,
                    appreciation_libre=item.appreciation_libre,
                    appreciation_auto=auto,
                )
            )
            db.add(
                HistoriqueNote(
                    evaluation_id=evaluation_id,
                    eleve_id=item.eleve_id,
                    annee_scolaire_id=evaluation.annee_scolaire_id,
                    ancienne_valeur=None,
                    nouvelle_valeur=new_valeur,
                    ancien_absent=None,
                    nouveau_absent=item.is_absent,
                    modifie_par_id=user_id,
                    ip_address=ip_address,
                )
            )
            changes += 1

    if changes:
        await audit_service.log_audit(
            db,
            action="update",
            resource_type="notes",
            resource_id=str(evaluation_id),
            details=f"{changes} note(s) modifiée(s) — {evaluation.libelle}",
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
        )

    await db.commit()
    return await get_grille_notes(db, evaluation_id)


async def _matiere_coef_map(db: AsyncSession, niveau_id: UUID) -> dict[UUID, Decimal]:
    result = await db.execute(
        select(Matiere.id, matiere_niveaux.c.coefficient)
        .join(matiere_niveaux, Matiere.id == matiere_niveaux.c.matiere_id)
        .where(matiere_niveaux.c.niveau_id == niveau_id)
    )
    return {row[0]: Decimal(str(row[1])) for row in result.all()}


async def get_moyennes_classe(
    db: AsyncSession,
    classe_id: UUID,
    periode_id: UUID,
) -> MoyennesClasseResponse:
    result = await db.execute(
        select(Classe).where(Classe.id == classe_id)
    )
    classe = result.scalar_one_or_none()
    if classe is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    periode = await db.get(Periode, periode_id)
    if periode is None:
        raise HTTPException(status_code=404, detail="Période introuvable")

    bareme = await _get_bareme(db, classe.annee_scolaire_id)
    coef_matieres = await _matiere_coef_map(db, classe.niveau_id)
    verrouille = await _is_verrouille(db, classe_id, periode_id)

    ev_result = await db.execute(
        select(Evaluation)
        .options(selectinload(Evaluation.notes))
        .where(
            Evaluation.classe_id == classe_id,
            Evaluation.periode_id == periode_id,
        )
    )
    evaluations = list(ev_result.scalars().all())

    eleves_data = await classe_service.list_eleves_classe(db, classe_id)
    eleves_items: list[EleveMoyennesItem] = []

    for eleve in eleves_data.eleves:
        moyennes_mat: list[MoyenneMatiereItem] = []
        matiere_ids = {ev.matiere_id for ev in evaluations}

        for mat_id in matiere_ids:
            mat = await db.get(Matiere, mat_id)
            if mat is None:
                continue
            evs = [ev for ev in evaluations if ev.matiere_id == mat_id]
            total = Decimal("0")
            total_coef = Decimal("0")
            for ev in evs:
                note = next((n for n in ev.notes if n.eleve_id == eleve.id), None)
                if note is None or note.is_absent or note.valeur is None:
                    continue
                total += note.valeur * ev.coefficient
                total_coef += ev.coefficient

            moy = _round_note(total / total_coef, bareme) if total_coef > 0 else None
            moyennes_mat.append(
                MoyenneMatiereItem(
                    matiere_id=mat_id,
                    matiere_code=mat.code,
                    matiere_libelle=mat.libelle,
                    coefficient_matiere=coef_matieres.get(mat_id, mat.coefficient_defaut),
                    moyenne=moy,
                    appreciation_auto=_auto_appreciation(moy, bareme) if moy is not None else None,
                )
            )

        mg_num = Decimal("0")
        mg_den = Decimal("0")
        for mm in moyennes_mat:
            if mm.moyenne is not None:
                mg_num += mm.moyenne * mm.coefficient_matiere
                mg_den += mm.coefficient_matiere

        moy_gen = _round_note(mg_num / mg_den, bareme) if mg_den > 0 else None
        eleves_items.append(
            EleveMoyennesItem(
                eleve_id=eleve.id,
                matricule=eleve.matricule,
                nom=eleve.nom,
                prenoms=eleve.prenoms,
                moyennes_matieres=moyennes_mat,
                moyenne_generale=moy_gen,
                appreciation_generale=_auto_appreciation(moy_gen, bareme) if moy_gen else None,
                rang=None,
            )
        )

    ranked = sorted(
        [e for e in eleves_items if e.moyenne_generale is not None],
        key=lambda x: x.moyenne_generale or Decimal("0"),
        reverse=True,
    )
    rank = 0
    prev: Decimal | None = None
    for i, e in enumerate(ranked):
        if e.moyenne_generale != prev:
            rank = i + 1
            prev = e.moyenne_generale
        for orig in eleves_items:
            if orig.eleve_id == e.eleve_id:
                orig.rang = rank

    return MoyennesClasseResponse(
        classe_id=classe_id,
        classe_nom=classe.nom,
        periode_id=periode_id,
        periode_libelle=periode.libelle,
        verrouille=verrouille,
        eleves=eleves_items,
    )


async def valider_periode(
    db: AsyncSession,
    classe_id: UUID,
    periode_id: UUID,
    user_id: UUID,
    verrouiller: bool = True,
) -> ValidationResponse:
    classe = await db.get(Classe, classe_id)
    if classe is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    result = await db.execute(
        select(ValidationPeriode).where(
            ValidationPeriode.classe_id == classe_id,
            ValidationPeriode.periode_id == periode_id,
        )
    )
    validation = result.scalar_one_or_none()
    if validation is None:
        validation = ValidationPeriode(
            classe_id=classe_id,
            periode_id=periode_id,
            annee_scolaire_id=classe.annee_scolaire_id,
        )
        db.add(validation)

    validation.verrouille = verrouiller
    validation.valide_par_id = user_id if verrouiller else None
    validation.date_validation = date.today() if verrouiller else None
    await db.commit()
    await db.refresh(validation)
    return ValidationResponse.model_validate(validation)


async def list_evaluations(
    db: AsyncSession,
    classe_id: UUID,
    matiere_id: UUID,
    periode_id: UUID,
) -> list[EvaluationResponse]:
    result = await db.execute(
        select(Evaluation)
        .options(selectinload(Evaluation.type_evaluation))
        .where(
            Evaluation.classe_id == classe_id,
            Evaluation.matiere_id == matiere_id,
            Evaluation.periode_id == periode_id,
        )
    )
    return [EvaluationResponse.model_validate(e) for e in result.scalars().all()]
