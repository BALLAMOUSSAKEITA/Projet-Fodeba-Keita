from datetime import date
from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from app.core.etablissement_defaults import (
    ADRESSE,
    LIEU_DELIVRANCE,
    NOM,
    format_telephone_affichage,
    telephone_etablissement,
)
from app.models.eleve import Eleve
from app.models.parametrage import Etablissement


def _etab_adresse_ligne(etab: Etablissement | None) -> str:
    if etab and etab.adresse:
        return etab.adresse.strip()
    if etab and etab.commune:
        return f"Commune de {etab.commune}, Conakry"
    return ADRESSE


def _lieu_delivrance(etab: Etablissement | None) -> str:
    if etab and etab.commune:
        return f"{etab.commune}, Conakry"
    return LIEU_DELIVRANCE


def _draw_header(c: canvas.Canvas, etab: Etablissement | None, title: str) -> None:
    c.setFont("Helvetica-Bold", 14)
    nom = etab.nom if etab else NOM
    c.drawCentredString(A4[0] / 2, A4[1] - 2 * cm, nom)
    c.setFont("Helvetica", 10)
    c.drawCentredString(A4[0] / 2, A4[1] - 2.55 * cm, _etab_adresse_ligne(etab))
    tel = format_telephone_affichage(telephone_etablissement(etab.telephone if etab else None))
    c.drawCentredString(A4[0] / 2, A4[1] - 3.1 * cm, f"Tél. {tel}")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(A4[0] / 2, A4[1] - 4 * cm, title)
    c.line(2 * cm, A4[1] - 4.45 * cm, A4[0] - 2 * cm, A4[1] - 4.45 * cm)


def generate_attestation_scolarite(eleve: Eleve, etab: Etablissement | None, annee_libelle: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_header(c, etab, "ATTESTATION DE SCOLARITÉ")

    y = A4[1] - 5.95 * cm
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
        f"Fait à {_lieu_delivrance(etab)}, le {date.today().strftime('%d/%m/%Y')}",
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

    y = A4[1] - 5.95 * cm
    c.setFont("Helvetica", 11)
    lines = [
        f"L'élève {eleve.prenoms} {eleve.nom}, matricule {eleve.matricule},",
        f"né(e) le {eleve.date_naissance}, est libéré(e) de notre établissement",
        f"pour continuer ses études à : {ecole_destination}.",
        "",
        "Nous certifions qu'il/elle ne présente aucune objection de notre part.",
        "",
        f"Fait à {_lieu_delivrance(etab)}, le {date.today().strftime('%d/%m/%Y')}",
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


def _format_gnf(amount) -> str:
    return f"{float(amount):,.0f} GNF".replace(",", " ")


def _paiement_date_str(paiement) -> str:
    d = paiement.date_paiement
    if hasattr(d, "strftime"):
        return d.strftime("%d/%m/%Y")
    return str(d)


def _draw_recu_detail_row(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    label: str,
    value: str,
    *,
    alt: bool = False,
    value_bold: bool = False,
) -> float:
    row_h = 0.72 * cm
    if alt:
        c.setFillColor(HexColor("#fafafa"))
        c.rect(x, y - row_h + 0.12 * cm, width, row_h, fill=1, stroke=0)
    c.setFillColor(HexColor("#71717a"))
    c.setFont("Helvetica", 9)
    c.drawString(x + 0.35 * cm, y - 0.48 * cm, label)
    c.setFillColor(HexColor("#18181b"))
    c.setFont("Helvetica-Bold" if value_bold else "Helvetica", 9)
    c.drawRightString(x + width - 0.35 * cm, y - 0.48 * cm, value)
    return y - row_h


def generate_recu_paiement(
    paiement,
    etab: Etablissement | None,
    *,
    annee_libelle: str = "",
    classe_nom: str | None = None,
) -> bytes:
    mode_labels = {
        "especes": "Espèces",
        "orange_money": "Orange Money",
        "mtn_momo": "MTN MoMo",
        "virement": "Virement bancaire",
        "cheque": "Chèque",
    }

    obsidian = HexColor("#14532d")
    accent = HexColor("#047857")
    border = HexColor("#d1fae5")
    muted = HexColor("#4b5563")

    card_w = 16 * cm
    card_h = 20.5 * cm
    card_x = (A4[0] - card_w) / 2
    card_y = A4[1] - 2.8 * cm - card_h

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    c.setFillColor(HexColor("#d4d4d8"))
    c.roundRect(card_x + 0.12 * cm, card_y - 0.12 * cm, card_w, card_h, 10, fill=1, stroke=0)

    c.setFillColor(HexColor("#ffffff"))
    c.setStrokeColor(border)
    c.setLineWidth(0.5)
    c.roundRect(card_x, card_y, card_w, card_h, 10, fill=1, stroke=1)

    header_h = 3.4 * cm
    header_y = card_y + card_h - header_h
    c.setFillColor(obsidian)
    c.rect(card_x, header_y, card_w, header_h, fill=1, stroke=0)
    c.setFillColor(accent)
    c.rect(card_x, header_y, card_w, 0.18 * cm, fill=1, stroke=0)

    nom = etab.nom if etab else NOM
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(card_x + card_w / 2, header_y + header_h - 1.35 * cm, nom)
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#bbf7d0"))
    c.drawCentredString(card_x + card_w / 2, header_y + header_h - 1.95 * cm, "REÇU DE PAIEMENT — SCOLARITÉ")

    tel = format_telephone_affichage(telephone_etablissement(etab.telephone if etab else None))
    contact_parts: list[str] = [_etab_adresse_ligne(etab), f"Tél. {tel}"]
    if etab and etab.email:
        contact_parts.append(str(etab.email))
    if contact_parts:
        c.setFont("Helvetica", 7)
        c.setFillColor(HexColor("#71717a"))
        c.drawCentredString(
            card_x + card_w / 2,
            header_y + 0.55 * cm,
            " · ".join(contact_parts)[:95],
        )

    meta_y = header_y - 0.85 * cm
    c.setFillColor(muted)
    c.setFont("Helvetica", 8)
    c.drawString(card_x + 0.6 * cm, meta_y, f"Date d'émission · {_paiement_date_str(paiement)}")
    c.setFillColor(obsidian)
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(card_x + card_w - 0.6 * cm, meta_y, paiement.numero_recu)

    eleve_nom = f"{paiement.eleve_prenoms} {paiement.eleve_nom}".strip()
    block_y = meta_y - 1.1 * cm
    c.setFillColor(HexColor("#fafafa"))
    c.setStrokeColor(border)
    c.roundRect(card_x + 0.6 * cm, block_y - 1.35 * cm, card_w - 1.2 * cm, 1.35 * cm, 6, fill=1, stroke=1)
    c.setFillColor(accent)
    c.rect(card_x + 0.6 * cm, block_y - 1.35 * cm, 0.12 * cm, 1.35 * cm, fill=1, stroke=0)
    c.setFillColor(muted)
    c.setFont("Helvetica", 8)
    c.drawString(card_x + 1 * cm, block_y - 0.45 * cm, "ÉLÈVE")
    c.setFillColor(obsidian)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(card_x + 1 * cm, block_y - 0.95 * cm, eleve_nom[:42])
    c.setFont("Helvetica", 9)
    c.setFillColor(muted)
    c.drawRightString(card_x + card_w - 0.85 * cm, block_y - 0.95 * cm, f"Matricule {paiement.eleve_matricule}")

    table_x = card_x + 0.6 * cm
    table_w = card_w - 1.2 * cm
    y = block_y - 1.75 * cm

    rows: list[tuple[str, str]] = []
    if annee_libelle:
        rows.append(("Année scolaire", annee_libelle))
    if classe_nom:
        rows.append(("Classe", classe_nom))
    rows.append(("Nature des frais", paiement.type_frais_libelle))
    if paiement.tranche_libelle:
        rows.append(("Tranche", paiement.tranche_libelle))
    if paiement.libelle:
        rows.append(("Libellé", paiement.libelle[:48]))
    rows.append(("Mode de règlement", mode_labels.get(paiement.mode_paiement, paiement.mode_paiement)))
    if paiement.reference_externe:
        rows.append(("Référence transaction", paiement.reference_externe))
    if paiement.remise_montant and float(paiement.remise_montant) > 0:
        rows.append(("Remise accordée", _format_gnf(paiement.remise_montant)))

    for i, (label, value) in enumerate(rows):
        y = _draw_recu_detail_row(c, table_x, y, table_w, label, value, alt=i % 2 == 0)

    amount_box_h = 2.1 * cm
    amount_y = y - 0.35 * cm - amount_box_h
    c.setFillColor(accent)
    c.roundRect(table_x, amount_y, table_w, amount_box_h, 8, fill=1, stroke=0)
    c.setFillColor(HexColor("#a1a1aa"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(table_x + table_w / 2, amount_y + amount_box_h - 0.65 * cm, "MONTANT ENCAISSÉ")
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(table_x + table_w / 2, amount_y + 0.55 * cm, _format_gnf(paiement.montant))

    qr_data = f"GSP|{paiement.numero_recu}|{paiement.eleve_matricule}|{paiement.montant}"
    footer_y = amount_y - 0.5 * cm
    qr_size = 2.6 * cm
    qr_x = table_x
    qr_bottom = footer_y - qr_size - 0.35 * cm

    try:
        import qrcode
        from reportlab.lib.utils import ImageReader

        qr = qrcode.make(qr_data, box_size=4, border=1)
        qr_buffer = BytesIO()
        qr.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        c.setStrokeColor(border)
        c.setLineWidth(0.5)
        c.roundRect(qr_x, qr_bottom, qr_size, qr_size, 4, fill=0, stroke=1)
        c.drawImage(ImageReader(qr_buffer), qr_x + 0.15 * cm, qr_bottom + 0.15 * cm, width=qr_size - 0.3 * cm, height=qr_size - 0.3 * cm)
    except ImportError:
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(muted)
        c.drawString(qr_x, qr_bottom + qr_size / 2, "QR code indisponible")

    c.setFillColor(muted)
    c.setFont("Helvetica", 7)
    c.drawString(qr_x, qr_bottom - 0.35 * cm, "Scan pour vérifier l'authenticité")

    sig_x = table_x + table_w - 6.2 * cm
    sig_y = footer_y - 0.2 * cm
    c.setFillColor(muted)
    c.setFont("Helvetica", 8)
    c.drawString(sig_x, sig_y, "Signature et cachet")
    c.setStrokeColor(border)
    c.setLineWidth(0.5)
    c.line(sig_x, sig_y - 1.35 * cm, sig_x + 5.8 * cm, sig_y - 1.35 * cm)
    c.setFont("Helvetica", 7)
    c.drawString(sig_x, sig_y - 1.65 * cm, "La caisse / Le responsable financier")

    c.setFillColor(muted)
    c.setFont("Helvetica-Oblique", 7)
    c.drawCentredString(
        card_x + card_w / 2,
        card_y + 0.45 * cm,
        "Document généré par GSP — Conservez ce reçu comme preuve de paiement.",
    )

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
