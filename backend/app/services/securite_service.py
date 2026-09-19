from pathlib import Path

from app.core.config import settings
from app.schemas.securite import SauvegardeStatusResponse

BACKUP_DIR = Path(__file__).resolve().parents[2] / "backups"


def get_sauvegarde_status() -> SauvegardeStatusResponse:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    dumps = sorted(
        list(BACKUP_DIR.glob("sgep_*.sql.gz")) + list(BACKUP_DIR.glob("sgep_*.zip")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    derniere = None
    taille = None
    if dumps:
        derniere = dumps[0].name
        taille = dumps[0].stat().st_size
    return SauvegardeStatusResponse(
        repertoire=str(BACKUP_DIR),
        derniere_sauvegarde=derniere,
        taille_octets=taille,
        chiffrement="GPG optionnel (voir scripts/backup-db.ps1)",
        procedure_restauration="docs/SAUVEGARDE_RESTAURATION.md",
        https_requis=settings.ENVIRONMENT != "development",
    )
