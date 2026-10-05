import csv
import io
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comptabilite import CategorieDepense, Depense, StatutDepense
from app.models.paiements import Paiement, StatutPaiement
from app.models.parametrage import Classe
from app.models.personnel import Personnel, StatutPersonnel
from app.schemas.rapports import (
    DashboardKPIResponse,
    GraphiquesResponse,
    RapportEffectifsResponse,
    SerieGraphique,
    StatistiquesAnnuellesResponse,
)
from app.services import classe_service, comptabilite_service, eleve_service, paiements_service, parametrage_service, pdf_service


def _month_start(d: date) -> date:
    return d.replace(day=1)


async def get_dashboard_kpis(db: AsyncSession) -> DashboardKPIResponse:
    annee = await parametrage_service.get_annee_active(db)
    annee_libelle = annee.libelle if annee else "—"

    stats = await eleve_service.get_stats_effectifs(db)

    classes_count = 0
    if annee:
        r = await db.execute(
            select(func.count()).select_from(Classe).where(Classe.annee_scolaire_id == annee.id)
        )
        classes_count = r.scalar_one()

    pers_count = (
        await db.execute(
            select(func.count()).select_from(Personnel).where(Personnel.statut == StatutPersonnel.ACTIF.value)
        )
    ).scalar_one()

    today = date.today()
    debut_mois = _month_start(today)
    recettes_mois = Decimal("0")
    if annee:
        recettes_mois = Decimal(str((
            await db.execute(
                select(func.coalesce(func.sum(Paiement.montant), 0)).where(
                    Paiement.annee_scolaire_id == annee.id,
                    Paiement.statut == StatutPaiement.VALIDE.value,
                    Paiement.date_paiement >= debut_mois,
                    Paiement.date_paiement <= today,
                    Paiement.montant > 0,
                )
            )
        ).scalar_one()))

    impayes = await paiements_service.list_impayes(db, annee.id if annee else None)
    total_impayes = sum((i.montant_restant for i in impayes), Decimal("0"))

    return DashboardKPIResponse(
        annee_libelle=annee_libelle,
        total_eleves=stats.total_eleves,
        total_classes=classes_count,
        total_personnel=pers_count,
        recettes_mois=recettes_mois,
        total_impayes=total_impayes,
        taux_presence_mois=None,
        nombre_impayes=len(impayes),
    )


async def get_rapport_effectifs(db: AsyncSession) -> RapportEffectifsResponse:
    annee = await parametrage_service.get_annee_active(db)
    stats = await eleve_service.get_stats_effectifs(db)
    par_classe = await classe_service.get_classe_effectifs(db, annee.id if annee else None)
    return RapportEffectifsResponse(
        annee_libelle=annee.libelle if annee else "—",
        stats=stats,
        par_classe=[c.model_dump() for c in par_classe],
    )


async def get_statistiques_annuelles(db: AsyncSession) -> StatistiquesAnnuellesResponse:
    annee = await parametrage_service.get_annee_active(db)
    if annee is None:
        raise HTTPException(status_code=404, detail="Année scolaire active introuvable")

    etab = await parametrage_service.get_etablissement(db)
    stats = await eleve_service.get_stats_effectifs(db)
    classes_count = (
        await db.execute(
            select(func.count()).select_from(Classe).where(Classe.annee_scolaire_id == annee.id)
        )
    ).scalar_one()

    fin = date.today()
    rapport = await comptabilite_service.get_rapport_financier(db, annee.date_debut, fin, annee.id)
    impayes = await paiements_service.list_impayes(db, annee.id)

    return StatistiquesAnnuellesResponse(
        etablissement=etab.nom if etab else "Groupe Scolaire Privé Fodeba Keita",
        annee_libelle=annee.libelle,
        total_eleves=stats.total_eleves,
        total_garcons=stats.total_garcons,
        total_filles=stats.total_filles,
        total_classes=classes_count,
        total_recettes=rapport.total_recettes,
        total_depenses=rapport.total_depenses,
        solde_financier=rapport.solde,
        moyenne_generale_etablissement=None,
        taux_reussite_global=None,
        taux_presence_annuel=None,
        nombre_impayes=len(impayes),
    )


async def get_graphiques(db: AsyncSession) -> GraphiquesResponse:
    annee = await parametrage_service.get_annee_active(db)
    stats = await eleve_service.get_stats_effectifs(db)

    effectifs = SerieGraphique(
        labels=[n.niveau_libelle for n in stats.par_niveau],
        values=[float(n.total) for n in stats.par_niveau],
    )
    sexe = SerieGraphique(
        labels=["Garçons", "Filles"],
        values=[float(stats.total_garcons), float(stats.total_filles)],
    )

    recettes_mois = SerieGraphique(labels=[], values=[])
    if annee:
        result = await db.execute(
            select(extract("month", Paiement.date_paiement), func.sum(Paiement.montant))
            .where(
                Paiement.annee_scolaire_id == annee.id,
                Paiement.statut == StatutPaiement.VALIDE.value,
                Paiement.montant > 0,
            )
            .group_by(extract("month", Paiement.date_paiement))
            .order_by(extract("month", Paiement.date_paiement))
        )
        mois_noms = ["", "Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        for mois, montant in result.all():
            recettes_mois.labels.append(mois_noms[int(mois)])
            recettes_mois.values.append(float(montant))

    depenses = SerieGraphique(labels=[], values=[])
    if annee:
        dep_result = await db.execute(
            select(CategorieDepense.libelle, func.sum(Depense.montant))
            .join(Depense, Depense.categorie_id == CategorieDepense.id)
            .where(
                Depense.annee_scolaire_id == annee.id,
                Depense.statut == StatutDepense.VALIDEE.value,
            )
            .group_by(CategorieDepense.libelle)
        )
        for libelle, montant in dep_result.all():
            depenses.labels.append(libelle)
            depenses.values.append(float(montant))

    return GraphiquesResponse(
        effectifs_par_niveau=effectifs,
        recettes_par_mois=recettes_mois,
        repartition_sexe=sexe,
        depenses_par_categorie=depenses,
    )


def export_csv_effectifs(rapport: RapportEffectifsResponse) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Rapport effectifs", rapport.annee_libelle])
    writer.writerow(["Total élèves", rapport.stats.total_eleves])
    writer.writerow(["Garçons", rapport.stats.total_garcons])
    writer.writerow(["Filles", rapport.stats.total_filles])
    writer.writerow([])
    writer.writerow(["Niveau", "Total", "Garçons", "Filles"])
    for n in rapport.stats.par_niveau:
        writer.writerow([n.niveau_libelle, n.total, n.garcons, n.filles])
    writer.writerow([])
    writer.writerow(["Classe", "Niveau", "Effectif", "Capacité", "Places restantes"])
    for c in rapport.par_classe:
        writer.writerow([c.get("nom"), c.get("niveau_libelle"), c.get("effectif"), c.get("capacite_max"), c.get("places_restantes")])
    return output.getvalue().encode("utf-8-sig")


async def export_excel_rapport(db: AsyncSession, rapport_type: str, **kwargs) -> bytes:
    from io import BytesIO

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active

    if rapport_type == "effectifs":
        data = await get_rapport_effectifs(db)
        ws.title = "Effectifs"
        ws.append(["Année", data.annee_libelle])
        ws.append(["Total élèves", data.stats.total_eleves])
        for n in data.stats.par_niveau:
            ws.append([n.niveau_libelle, n.total, n.garcons, n.filles])
        ws2 = wb.create_sheet("Classes")
        ws2.append(["Classe", "Niveau", "Effectif", "Capacité"])
        for c in data.par_classe:
            ws2.append([c.get("nom"), c.get("niveau_libelle"), c.get("effectif"), c.get("capacite_max")])
    elif rapport_type == "financier":
        date_debut = kwargs["date_debut"]
        date_fin = kwargs["date_fin"]
        annee_id = kwargs.get("annee_id")
        rapport = await comptabilite_service.get_rapport_financier(db, date_debut, date_fin, annee_id)
        ws.title = "Financier"
        ws.append(["Période", f"{date_debut} → {date_fin}"])
        ws.append(["Recettes", float(rapport.total_recettes)])
        ws.append(["Dépenses", float(rapport.total_depenses)])
        ws.append(["Solde", float(rapport.solde)])
    elif rapport_type == "annuel":
        data = await get_statistiques_annuelles(db)
        ws.title = "Statistiques annuelles"
        for row in [
            ["Établissement", data.etablissement],
            ["Année", data.annee_libelle],
            ["Effectif total", data.total_eleves],
            ["Recettes", float(data.total_recettes)],
            ["Dépenses", float(data.total_depenses)],
            ["Solde", float(data.solde_financier)],
            ["Impayés (élèves)", data.nombre_impayes],
        ]:
            ws.append(row)
    else:
        raise HTTPException(status_code=422, detail="Type de rapport inconnu")

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()


async def export_pdf_rapport(db: AsyncSession, rapport_type: str, **kwargs) -> bytes:
    etab = await parametrage_service.get_etablissement(db)
    lines: list[str] = []

    if rapport_type == "effectifs":
        data = await get_rapport_effectifs(db)
        lines = [
            f"Année scolaire : {data.annee_libelle}",
            f"Total élèves : {data.stats.total_eleves}",
            f"Garçons : {data.stats.total_garcons} | Filles : {data.stats.total_filles}",
            "",
            "Par niveau :",
        ]
        for n in data.stats.par_niveau:
            lines.append(f"  • {n.niveau_libelle} : {n.total} ({n.garcons} G / {n.filles} F)")
        title = "RAPPORT DES EFFECTIFS"
    elif rapport_type == "financier":
        date_debut = kwargs["date_debut"]
        date_fin = kwargs["date_fin"]
        annee_id = kwargs.get("annee_id")
        r = await comptabilite_service.get_rapport_financier(db, date_debut, date_fin, annee_id)
        lines = [
            f"Période : {date_debut} → {date_fin}",
            f"Total recettes : {r.total_recettes:,.0f} GNF",
            f"Total dépenses : {r.total_depenses:,.0f} GNF",
            f"Solde : {r.solde:,.0f} GNF",
        ]
        title = "RAPPORT FINANCIER"
    elif rapport_type == "annuel":
        data = await get_statistiques_annuelles(db)
        lines = [
            f"Établissement : {data.etablissement}",
            f"Année : {data.annee_libelle}",
            f"Effectif : {data.total_eleves} élèves ({data.total_garcons} G / {data.total_filles} F)",
            f"Classes : {data.total_classes}",
            f"Recettes : {data.total_recettes:,.0f} GNF",
            f"Dépenses : {data.total_depenses:,.0f} GNF",
            f"Solde : {data.solde_financier:,.0f} GNF",
            f"Impayés : {data.nombre_impayes} élève(s)",
        ]
        title = "STATISTIQUES ANNUELLES — DRE / INSPECTION"
    else:
        raise HTTPException(status_code=422, detail="Type de rapport inconnu")

    return pdf_service.generate_rapport_texte(title, lines, etab)
