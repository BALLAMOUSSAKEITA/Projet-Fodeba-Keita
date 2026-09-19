from datetime import date
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from app.models.eleve import Eleve
from app.models.parametrage import Etablissement


def _draw_header(c: canvas.Canvas, etab: Etablissement | None, title: str) -> None:
    c.setFont("Helvetica-Bold", 14)
    nom = etab.nom if etab else "Groupe Scolaire Privé Fodeba Keita"
    c.drawCentredString(A4[0] / 2, A4[1] - 2 * cm, nom)
    c.setFont("Helvetica", 10)
    if etab and etab.adresse:
        c.drawCentredString(A4[0] / 2, A4[1] - 2.6 * cm, etab.adresse)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(A4[0] / 2, A4[1] - 3.6 * cm, title)
    c.line(2 * cm, A4[1] - 4 * cm, A4[0] - 2 * cm, A4[1] - 4 * cm)


def generate_attestation_scolarite(eleve: Eleve, etab: Etablissement | None, annee_libelle: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, "ATTESTATION DE SCOLARITÉ")

    y = A4[1] - 5.5 * cm
    c.setFont("Helvetica", 11)
    lines = [
        "Je soussigné(e), Directeur du Groupe Scolaire Privé Fodeba Keita, certifie que :",
        "",
        f"Nom et prénoms : {eleve.prenoms} {eleve.nom}",
        f"Matricule : {eleve.matricule}",
        f"Né(e) le : {eleve.date_naissance} à {eleve.lieu_naissance or '—'}",
        f"Sexe : {'Masculin' if eleve.sexe == 'M' else 'Féminin'}",
        "",
        f"Est régulièrement inscrit(e) dans notre établissement pour l'année scolaire {annee_libelle}.",
        "",
        "La présente attestation est délivrée pour servir et valoir ce que de droit.",
        "",
        f"Fait à Conakry, le {date.today().strftime('%d/%m/%Y')}",
        "",
        "Le Directeur",
    ]
    for line in lines:
        c.drawString(2.5 * cm, y, line)
        y -= 0.7 * cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_certificat_transfert(
    eleve: Eleve,
    etab: Etablissement | None,
    ecole_destination: str,
) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, "CERTIFICAT DE TRANSFERT")

    y = A4[1] - 5.5 * cm
    c.setFont("Helvetica", 11)
    lines = [
        f"L'élève {eleve.prenoms} {eleve.nom}, matricule {eleve.matricule},",
        f"né(e) le {eleve.date_naissance}, est libéré(e) de notre établissement",
        f"pour continuer ses études à : {ecole_destination}.",
        "",
        "Nous certifions qu'il/elle ne présente aucune objection de notre part.",
        "",
        f"Fait à Conakry, le {date.today().strftime('%d/%m/%Y')}",
        "",
        "Le Directeur",
    ]
    for line in lines:
        c.drawString(2.5 * cm, y, line)
        y -= 0.7 * cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_liste_classe(
    classe_nom: str,
    eleves: list[tuple[str, str, str]],
    etab: Etablissement | None,
    annee_libelle: str,
) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, f"LISTE DES ÉLÈVES — {classe_nom} ({annee_libelle})")

    y = A4[1] - 5 * cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "N°")
    c.drawString(3 * cm, y, "Matricule")
    c.drawString(6.5 * cm, y, "Nom et prénoms")
    c.drawString(14 * cm, y, "Sexe")
    y -= 0.5 * cm
    c.line(2 * cm, y, A4[0] - 2 * cm, y)
    y -= 0.4 * cm

    c.setFont("Helvetica", 9)
    for i, (matricule, nom_complet, sexe) in enumerate(eleves, 1):
        if y < 2 * cm:
            c.showPage()
            y = A4[1] - 3 * cm
        c.drawString(2 * cm, y, str(i))
        c.drawString(3 * cm, y, matricule)
        c.drawString(6.5 * cm, y, nom_complet)
        c.drawString(14 * cm, y, sexe)
        y -= 0.5 * cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_edt_pdf(
    titre: str,
    jours: list[str],
    lignes: list,
    etab: Etablissement | None,
) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, titre)

    col_width = (A4[0] - 4 * cm) / (len(jours) + 1)
    x_start = 2 * cm
    y = A4[1] - 5 * cm
    row_height = 1.2 * cm

    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_start, y, "Créneau")
    for i, jour in enumerate(jours):
        c.drawString(x_start + (i + 1) * col_width, y, jour)
    y -= row_height

    c.setFont("Helvetica", 7)
    for ligne in lignes:
        creneau = ligne.creneau
        label = creneau.libelle
        label += f" {creneau.heure_debut.strftime('%H:%M')}-{creneau.heure_fin.strftime('%H:%M')}"
        c.drawString(x_start, y, label[:25])
        for i, seance in enumerate(ligne.cellules):
            if seance and seance.matiere:
                c.drawString(x_start + (i + 1) * col_width, y, seance.matiere.libelle[:18])
        y -= row_height
        if y < 2 * cm:
            c.showPage()
            y = A4[1] - 3 * cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def _draw_bulletin_notes(c, data, y_start: float) -> float:
    y = y_start
    c.setFont("Helvetica", 10)
    c.drawString(2.5 * cm, y, f"Élève : {data.prenoms} {data.nom}  —  Matricule : {data.matricule}")
    y -= 0.6 * cm
    c.drawString(2.5 * cm, y, f"Classe : {data.classe_nom}  —  {data.periode_libelle}  —  {data.annee_libelle}")
    y -= 1 * cm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2.5 * cm, y, "Matière")
    c.drawString(10 * cm, y, "Moyenne")
    c.drawString(13 * cm, y, "Appréciation")
    y -= 0.5 * cm
    c.setFont("Helvetica", 9)
    for m in data.moyennes.moyennes_matieres:
        c.drawString(2.5 * cm, y, m.matiere_libelle)
        c.drawString(10 * cm, y, str(m.moyenne) if m.moyenne else "—")
        c.drawString(13 * cm, y, (m.appreciation_auto or "—")[:30])
        y -= 0.45 * cm
    y -= 0.3 * cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2.5 * cm, y, f"Moyenne générale : {data.moyennes.moyenne_generale or '—'} / Rang : {data.moyennes.rang or '—'}")
    y -= 0.6 * cm
    c.drawString(2.5 * cm, y, f"Appréciation : {data.moyennes.appreciation_generale or '—'}")
    y -= 0.8 * cm
    if data.decision:
        c.drawString(2.5 * cm, y, f"Décision : {data.decision.upper()}")
        if data.observation:
            y -= 0.5 * cm
            c.drawString(2.5 * cm, y, f"Observation : {data.observation[:80]}")
    return y


def generate_bulletin_primaire(data, etab: Etablissement | None) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, "BULLETIN SCOLAIRE")
    _draw_bulletin_notes(c, data, A4[1] - 5 * cm)
    c.drawString(2.5 * cm, 3 * cm, "Le Directeur")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_bulletins_classe(bulletins: list, etab: Etablissement | None) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    for data in bulletins:
        _draw_header(c, etab, "BULLETIN SCOLAIRE")
        _draw_bulletin_notes(c, data, A4[1] - 5 * cm)
        c.drawString(2.5 * cm, 3 * cm, "Le Directeur")
        c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_bulletin_annuel(eleve, classe_nom, annee_libelle, trimestres, moy_annuelle, decision, etab) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, "BULLETIN ANNUEL")
    y = A4[1] - 5 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2.5 * cm, y, f"{eleve.prenoms} {eleve.nom} — {eleve.matricule}")
    y -= 0.6 * cm
    c.drawString(2.5 * cm, y, f"Classe : {classe_nom} — Année {annee_libelle}")
    y -= 1 * cm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2.5 * cm, y, "Trimestre")
    c.drawString(10 * cm, y, "Moyenne générale")
    y -= 0.5 * cm
    c.setFont("Helvetica", 9)
    for lib, moy in trimestres:
        c.drawString(2.5 * cm, y, lib)
        c.drawString(10 * cm, y, str(moy) if moy else "—")
        y -= 0.45 * cm
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2.5 * cm, y, f"Moyenne annuelle : {moy_annuelle or '—'}")
    if decision:
        y -= 0.6 * cm
        c.drawString(2.5 * cm, y, f"Décision de passage : {decision.upper()}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_bulletin_maternelle(eleve, grille, row, etab: Etablissement | None) -> bytes:
    statut_label = {"acquis": "Acquis", "en_cours": "En cours", "non_acquis": "Non acquis"}
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, "BULLETIN MATERNELLE")
    y = A4[1] - 5 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2.5 * cm, y, f"{eleve.prenoms} {eleve.nom} — {grille.classe_nom}")
    y -= 0.6 * cm
    c.drawString(2.5 * cm, y, grille.periode_libelle)
    y -= 1 * cm
    domaine = ""
    c.setFont("Helvetica", 9)
    for comp in grille.competences:
        if comp.domaine != domaine:
            domaine = comp.domaine
            y -= 0.3 * cm
            c.setFont("Helvetica-Bold", 9)
            c.drawString(2.5 * cm, y, domaine)
            y -= 0.5 * cm
            c.setFont("Helvetica", 9)
        stat = row.evaluations.get(str(comp.id))
        label = statut_label.get(stat, "—") if stat else "—"
        c.drawString(3 * cm, y, f"• {comp.libelle} : {label}")
        y -= 0.4 * cm
        if y < 2.5 * cm:
            c.showPage()
            y = A4[1] - 3 * cm
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_recu_paiement(paiement, etab: Etablissement | None) -> bytes:
    from io import BytesIO

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, "REÇU DE PAIEMENT")

    mode_labels = {
        "especes": "Espèces",
        "orange_money": "Orange Money",
        "mtn_momo": "MTN MoMo",
        "virement": "Virement bancaire",
        "cheque": "Chèque",
    }

    y = A4[1] - 5 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2.5 * cm, y, f"N° {paiement.numero_recu}")
    y -= 0.8 * cm
    c.setFont("Helvetica", 10)
    lines = [
        f"Date : {paiement.date_paiement.strftime('%d/%m/%Y') if hasattr(paiement.date_paiement, 'strftime') else paiement.date_paiement}",
        f"Élève : {paiement.eleve_prenoms} {paiement.eleve_nom}",
        f"Matricule : {paiement.eleve_matricule}",
        f"Objet : {paiement.type_frais_libelle}",
    ]
    if paiement.tranche_libelle:
        lines.append(f"Tranche : {paiement.tranche_libelle}")
    lines.extend([
        f"Montant : {paiement.montant:,.0f} GNF".replace(",", " "),
        f"Mode : {mode_labels.get(paiement.mode_paiement, paiement.mode_paiement)}",
    ])
    if paiement.reference_externe:
        lines.append(f"Référence : {paiement.reference_externe}")
    if paiement.remise_montant and paiement.remise_montant > 0:
        lines.append(f"Remise appliquée : {paiement.remise_montant:,.0f} GNF".replace(",", " "))

    for line in lines:
        c.drawString(2.5 * cm, y, line)
        y -= 0.6 * cm

    qr_data = f"SGEP|{paiement.numero_recu}|{paiement.eleve_matricule}|{paiement.montant}"
    y -= 0.5 * cm
    c.setFont("Helvetica", 8)
    c.drawString(2.5 * cm, y, f"Vérification : {qr_data}")
    y -= 1 * cm

    try:
        import qrcode
        from reportlab.lib.utils import ImageReader

        qr = qrcode.make(qr_data, box_size=4, border=2)
        qr_buffer = BytesIO()
        qr.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        c.drawImage(ImageReader(qr_buffer), A4[0] - 5 * cm, y - 3 * cm, width=3 * cm, height=3 * cm)
    except ImportError:
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(2.5 * cm, y, "(QR code — installer qrcode pour l'affichage graphique)")

    y -= 1.5 * cm
    c.setFont("Helvetica", 9)
    c.drawString(2.5 * cm, y, "Signature et cachet de l'établissement")
    c.line(2.5 * cm, y - 0.3 * cm, 8 * cm, y - 0.3 * cm)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_bulletin_paie(bulletin, etab: Etablissement | None) -> bytes:
    from io import BytesIO

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, "BULLETIN DE PAIE")

    y = A4[1] - 5 * cm
    c.setFont("Helvetica", 10)
    lines = [
        f"Période : {bulletin.periode_libelle}",
        f"Employé : {bulletin.personnel_prenoms} {bulletin.personnel_nom}",
        f"Matricule : {bulletin.personnel_matricule}",
        "",
        "── Éléments de rémunération ──",
        f"Salaire de base : {float(bulletin.salaire_base):,.0f} GNF".replace(",", " "),
        f"Prime ancienneté : {float(bulletin.prime_anciennete):,.0f} GNF".replace(",", " "),
        f"Autres primes : {float(bulletin.prime_autre):,.0f} GNF".replace(",", " "),
        f"Indemnité transport : {float(bulletin.indemnite_transport):,.0f} GNF".replace(",", " "),
        f"Indemnité logement : {float(bulletin.indemnite_logement):,.0f} GNF".replace(",", " "),
        f"Salaire brut : {float(bulletin.brut):,.0f} GNF".replace(",", " "),
        "",
        "── Retenues ──",
        f"CNSS (5 %) : {float(bulletin.retenue_cnss):,.0f} GNF".replace(",", " "),
        f"ITS (15 %) : {float(bulletin.retenue_its):,.0f} GNF".replace(",", " "),
        f"Absences ({bulletin.jours_absence} j) : {float(bulletin.retenue_absences):,.0f} GNF".replace(",", " "),
        f"Avances : {float(bulletin.retenue_avances):,.0f} GNF".replace(",", " "),
        f"Autres retenues : {float(bulletin.autres_retenues):,.0f} GNF".replace(",", " "),
        "",
        f"NET À PAYER : {float(bulletin.net_a_payer):,.0f} GNF".replace(",", " "),
        "",
        f"Statut : {bulletin.statut.upper()}",
    ]
    for line in lines:
        c.drawString(2.5 * cm, y, line)
        y -= 0.55 * cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_rapport_texte(title: str, lines: list[str], etab: Etablissement | None) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, title)

    y = A4[1] - 5.5 * cm
    c.setFont("Helvetica", 11)
    for line in lines:
        if y < 3 * cm:
            c.showPage()
            y = A4[1] - 3 * cm
            c.setFont("Helvetica", 11)
        c.drawString(2.5 * cm, y, line)
        y -= 0.6 * cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
