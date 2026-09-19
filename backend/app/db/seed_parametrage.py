from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
    TypeCalendrier,
    TypeFrais,
    TypeNiveau,
    TypePeriode,
)

NIVEAUX = [
    ("PS", "Petite Section", 1, TypeNiveau.MATERNELLE),
    ("MS", "Moyenne Section", 2, TypeNiveau.MATERNELLE),
    ("GS", "Grande Section", 3, TypeNiveau.MATERNELLE),
    ("1A", "1re Année", 4, TypeNiveau.PRIMAIRE),
    ("2A", "2e Année", 5, TypeNiveau.PRIMAIRE),
    ("3A", "3e Année", 6, TypeNiveau.PRIMAIRE),
    ("4A", "4e Année", 7, TypeNiveau.PRIMAIRE),
    ("5A", "5e Année", 8, TypeNiveau.PRIMAIRE),
    ("6A", "6e Année", 9, TypeNiveau.PRIMAIRE),
]

MATIERES_PRIMAIRE = [
    ("FR", "Français", Decimal("3")),
    ("MATH", "Mathématiques", Decimal("3")),
    ("SCI", "Sciences", Decimal("2")),
    ("HG", "Histoire-Géographie", Decimal("2")),
    ("ECM", "ECM", Decimal("1")),
    ("EPS", "EPS", Decimal("1")),
    ("DESSIN", "Dessin", Decimal("1")),
]

MATIERES_MATERNELLE = [
    ("EVEIL", "Éveil", Decimal("1")),
    ("LECT", "Lecture", Decimal("1")),
    ("ECRIT", "Écriture", Decimal("1")),
]

TYPES_FRAIS = [
    ("INSCRIPTION", "Inscription", "Frais d'inscription annuelle"),
    ("SCOLARITE", "Scolarité", "Frais de scolarité"),
    ("CANTINE", "Cantine", "Frais de cantine"),
    ("TRANSPORT", "Transport", "Transport scolaire"),
    ("FOURNITURES", "Fournitures", "Fournitures scolaires"),
    ("UNIFORME", "Uniforme", "Tenue scolaire"),
    ("EXAMEN", "Examen", "Frais d'examen CEE"),
]

REFERENTIELS = {
    "nationalite": [("GN", "Guinéenne"), ("SN", "Sénégalaise"), ("ML", "Malienne"), ("CI", "Ivoirienne")],
    "region": [
        ("CONAKRY", "Conakry"),
        ("KINDIA", "Kindia"),
        ("BOKÉ", "Boké"),
        ("LABÉ", "Labé"),
        ("FARANAH", "Faranah"),
        ("KANKAN", "Kankan"),
        ("MAMOU", "Mamou"),
        ("NZÉRÉKORÉ", "Nzérékoré"),
    ],
    "groupe_sanguin": [
        ("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-"),
    ],
}

CALENDRIER_2025 = [
    ("Fête de l'Indépendance", date(2025, 10, 2), date(2025, 10, 2), TypeCalendrier.FERIE),
    ("Vacances de Noël", date(2025, 12, 20), date(2026, 1, 5), TypeCalendrier.VACANCE),
    ("Vacances de Pâques", date(2026, 4, 6), date(2026, 4, 20), TypeCalendrier.VACANCE),
    ("Grands vacances", date(2026, 7, 1), date(2026, 9, 15), TypeCalendrier.VACANCE),
]


async def seed_parametrage(db: AsyncSession) -> None:
    result = await db.execute(select(Etablissement).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    etab = Etablissement(
        nom="Groupe Scolaire Privé Fodeba Keita",
        code="GSPFK",
        adresse="Commune de Ratoma, Conakry",
        region="Conakry",
        prefecture="Conakry",
        commune="Ratoma",
        telephone="+224621234567",
        email="contact@fodebakeita.gn",
        devise_principale="GNF",
    )
    db.add(etab)

    annee = AnneeScolaire(
        libelle="2025-2026",
        date_debut=date(2025, 9, 15),
        date_fin=date(2026, 7, 15),
        statut=StatutAnneeScolaire.ACTIVE.value,
        is_active=True,
    )
    db.add(annee)
    await db.flush()

    bareme = Bareme(
        annee_scolaire_id=annee.id,
        echelle="/20",
        arrondi_decimales=2,
        seuil_passage=Decimal("10"),
        seuil_redoublement=Decimal("8"),
    )
    db.add(bareme)

    niveau_map: dict[str, Niveau] = {}
    for code, libelle, ordre, type_n in NIVEAUX:
        niveau = Niveau(code=code, libelle=libelle, ordre=ordre, type=type_n.value)
        db.add(niveau)
        niveau_map[code] = niveau
    await db.flush()

    classes_config = [
        ("PS", "A"), ("MS", "A"), ("GS", "A"),
        ("1A", "A"), ("1A", "B"),
        ("2A", "A"), ("3A", "A"), ("4A", "A"),
        ("5A", "A"), ("6A", "A"),
    ]
    for niveau_code, section in classes_config:
        db.add(
            Classe(
                nom=f"{niveau_map[niveau_code].libelle} {section}",
                capacite_max=40,
                salle=f"Salle {niveau_code}{section}",
                niveau_id=niveau_map[niveau_code].id,
                annee_scolaire_id=annee.id,
            )
        )

    periodes = [
        ("1er Trimestre", date(2025, 9, 15), date(2025, 12, 19), 1),
        ("2e Trimestre", date(2026, 1, 6), date(2026, 3, 31), 2),
        ("3e Trimestre", date(2026, 4, 21), date(2026, 7, 15), 3),
    ]
    for libelle, debut, fin, ordre in periodes:
        db.add(
            Periode(
                libelle=libelle,
                type=TypePeriode.TRIMESTRE.value,
                date_debut=debut,
                date_fin=fin,
                ordre=ordre,
                annee_scolaire_id=annee.id,
            )
        )

    for code, libelle, coef in MATIERES_PRIMAIRE + MATIERES_MATERNELLE:
        matiere = Matiere(code=code, libelle=libelle, coefficient_defaut=coef)
        if code in ("EVEIL", "LECT", "ECRIT"):
            matiere.niveaux = [niveau_map[c] for c in ("PS", "MS", "GS")]
        else:
            matiere.niveaux = [niveau_map[c] for c in ("1A", "2A", "3A", "4A", "5A", "6A")]
        db.add(matiere)
    await db.flush()

    for code, libelle, desc in TYPES_FRAIS:
        db.add(TypeFrais(code=code, libelle=libelle, description=desc, actif=True))

    for libelle, debut, fin, type_cal in CALENDRIER_2025:
        db.add(
            CalendrierScolaire(
                libelle=libelle,
                date_debut=debut,
                date_fin=fin,
                type=type_cal.value,
                annee_scolaire_id=annee.id,
            )
        )

    for ref_type, items in REFERENTIELS.items():
        for code, libelle in items:
            db.add(Referentiel(type=ref_type, code=code, libelle=libelle))

    await db.flush()
