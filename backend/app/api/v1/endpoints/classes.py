from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_any_permission
from app.models.user import User
from app.schemas.classe import ClasseEffectifResponse, ClasseElevesResponse
from app.services import classe_service, parametrage_service, pdf_service

router = APIRouter()

READ_PERMISSIONS = ("students.view", "students.enroll", "reports.view_pedagogical")


@router.get("/effectifs", response_model=list[ClasseEffectifResponse])
async def get_effectifs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await classe_service.get_classe_effectifs(db)


@router.get("/{classe_id}/eleves", response_model=ClasseElevesResponse)
async def get_classe_eleves(
    classe_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    return await classe_service.list_eleves_classe(db, classe_id)


@router.get("/{classe_id}/liste-pdf")
async def download_liste_classe_pdf(
    classe_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_any_permission(*READ_PERMISSIONS)),
):
    data = await classe_service.list_eleves_classe(db, classe_id)
    etab = await parametrage_service.get_etablissement(db)
    annee = await parametrage_service.get_annee_active(db)
    annee_libelle = annee.libelle if annee else "—"

    eleves_data = [
        (e.matricule, f"{e.prenoms} {e.nom}", "G" if e.sexe == "M" else "F")
        for e in data.eleves
    ]
    pdf_bytes = pdf_service.generate_liste_classe(
        data.classe.nom, eleves_data, etab, annee_libelle
    )
    filename = f"liste_{data.classe.nom.replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
