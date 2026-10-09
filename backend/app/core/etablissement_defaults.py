"""Coordonnées officielles de l'établissement (référence code & PDF)."""

NOM = "Groupe Scolaire Privé Fodeba Keita"
CODE = "GSPFK"
ADRESSE = "Commune de Matam, Conakry"
COMMUNE = "Matam"
PREFECTURE = "Conakry"
REGION = "Conakry"
LIEU_DELIVRANCE = "Matam, Conakry"
# Numéro officiel établissement (Guinée)
TELEPHONE = "+224626137290"
TELEPHONE_AFFICHAGE = "626 137 290"


def format_telephone_affichage(telephone: str | None) -> str:
    if not telephone or not telephone.strip():
        return TELEPHONE_AFFICHAGE
    raw = telephone.strip().replace(" ", "").replace("-", "")
    if raw.startswith("+224"):
        digits = raw[4:]
    elif raw.startswith("224") and len(raw) > 9:
        digits = raw[3:]
    else:
        digits = raw.lstrip("+")
    if len(digits) == 9 and digits.isdigit():
        return f"{digits[0:3]} {digits[3:6]} {digits[6:9]}"
    return telephone.strip()


def telephone_etablissement(telephone: str | None) -> str:
    return (telephone or "").strip() or TELEPHONE
