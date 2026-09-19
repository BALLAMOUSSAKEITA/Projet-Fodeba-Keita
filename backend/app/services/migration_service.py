"""Import migration depuis fichiers CSV (export Excel)."""

import csv
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parametrage import Classe, Niveau
from app.schemas.eleve import EleveCreate, TuteurCreate
from app.schemas.personnel import PersonnelCreate
from app.services import eleve_service, parametrage_service, personnel_service


@dataclass
class ImportReport:
    created: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def _parse_date(value: str) -> date:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date invalide : {value}")


async def _resolve_niveau(db: AsyncSession, code: str) -> Niveau:
    result = await db.execute(select(Niveau).where(Niveau.code == code.strip().upper()))
    niveau = result.scalar_one_or_none()
    if niveau is None:
        raise ValueError(f"Niveau introuvable : {code}")
    return niveau


async def _resolve_classe(db: AsyncSession, nom: str, annee_id: UUID) -> Classe | None:
    if not nom or not nom.strip():
        return None
    result = await db.execute(
        select(Classe).where(Classe.nom == nom.strip(), Classe.annee_scolaire_id == annee_id)
    )
    return result.scalar_one_or_none()


async def import_eleves_csv(db: AsyncSession, csv_path: Path) -> ImportReport:
    report = ImportReport()
    annee = await parametrage_service.get_annee_active(db)

    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                niveau = await _resolve_niveau(db, row["niveau_code"])
                tuteur_type = row.get("tuteur_type", "pere").strip().lower()
                if tuteur_type not in ("pere", "mere", "tuteur"):
                    tuteur_type = "tuteur"

                data = EleveCreate(
                    nom=row["nom"].strip(),
                    prenoms=row["prenoms"].strip(),
                    sexe=row["sexe"].strip().upper(),
                    date_naissance=_parse_date(row["date_naissance"]),
                    lieu_naissance=row.get("lieu_naissance") or None,
                    adresse=row.get("adresse") or None,
                    niveau_id=niveau.id,
                    tuteurs=[
                        TuteurCreate(
                            type=tuteur_type,
                            nom=row["tuteur_nom"].strip(),
                            prenoms=row["tuteur_prenoms"].strip(),
                            telephone=row["tuteur_telephone"].strip(),
                        )
                    ],
                )
                eleve = await eleve_service.create_eleve(db, data)

                classe_nom = row.get("classe_nom", "")
                if classe_nom:
                    classe = await _resolve_classe(db, classe_nom, annee.id)
                    if classe:
                        await eleve_service.affecter_classe(db, eleve.id, classe.id)
                    else:
                        report.errors.append(f"Ligne {i} : classe '{classe_nom}' introuvable — élève créé sans classe")

                report.created += 1
            except Exception as exc:
                report.errors.append(f"Ligne {i} : {exc}")

    await db.commit()
    return report


async def import_personnel_csv(db: AsyncSession, csv_path: Path) -> ImportReport:
    report = ImportReport()

    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                categorie = row.get("categorie", "enseignant").strip().lower()
                if categorie not in ("enseignant", "non_enseignant"):
                    categorie = "enseignant"

                date_embauche = None
                if row.get("date_embauche"):
                    date_embauche = _parse_date(row["date_embauche"])

                date_naissance = None
                if row.get("date_naissance"):
                    date_naissance = _parse_date(row["date_naissance"])

                data = PersonnelCreate(
                    nom=row["nom"].strip(),
                    prenoms=row["prenoms"].strip(),
                    sexe=row.get("sexe", "M").strip().upper(),
                    telephone=row["telephone"].strip(),
                    email=row.get("email") or None,
                    categorie=categorie,
                    fonction=row.get("fonction") or None,
                    specialite=row.get("specialite") or None,
                    date_embauche=date_embauche,
                    date_naissance=date_naissance,
                )
                await personnel_service.create_personnel(db, data)
                report.created += 1
            except Exception as exc:
                report.errors.append(f"Ligne {i} : {exc}")

    await db.commit()
    return report


async def verify_migration(db: AsyncSession) -> dict:
    annee = await parametrage_service.get_annee_active(db)
    eleves, total_eleves = await eleve_service.list_eleves(db, limit=1)
    classes = await parametrage_service.list_classes(db, annee.id)

    from app.models.personnel import Personnel

    personnel_count = (
        await db.execute(select(func.count()).select_from(Personnel))
    ).scalar_one()

    return {
        "annee_active": annee.libelle,
        "total_eleves": total_eleves,
        "total_classes": len(classes),
        "total_personnel": personnel_count,
        "sample_eleve": eleves[0].matricule if eleves else None,
    }
