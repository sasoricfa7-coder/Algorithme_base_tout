import json
import sys
from erreur import gestion as erreur
from utils import sans_accents
import os


def verificateur() -> str:
    if len(sys.argv) < 2:
        erreur("Aucun fichier indiqué // No file provided 📁")
    nom: str = sys.argv[1]

    if not os.path.isfile(nom):
        erreur(f"Le fichier {nom} n'existe pas // File {nom} not found 🔍")

    return nom


def charger_code(nom: str) -> str:
    with open(nom, "r", encoding="utf-8") as f:
        return f.read()


def charger_json(nom: str) -> dict:
    with open(nom, "r", encoding="utf-8") as f:
        contenu = json.load(f)
    return contenu


def construire_table(le_json: dict) -> dict[str, str]:
    """
    Construit une table unique : mot normalisé -> type de token.
    Fusionne toutes les listes alphabétiques du JSON.
    """
    table: dict[str, str] = {}
    for cle, type_ in (
        ("mots_cles",              "mots_cles"),
        ("operateurs_logiques",    "operateurs_logiques"),
        ("operateurs_arihmetiques", "operateurs_arihmetiques"),
        ("valeur_booleen",         "valeur_booleen"),
    ):
        for mot in le_json[cle]:
            table[sans_accents(mot)] = type_
    return table


def main() -> tuple[str, dict]:
    nom: str = verificateur()
    code_source: str = charger_code(nom)
    fichier_json: dict = charger_json("langage.json")

    if code_source.strip() == "":
        erreur(f"{nom} est vide // {nom} is empty 🕳️")

    # ✅ pré-calcul unique : la table sera réutilisée à chaque appel d'alpha
    fichier_json["table_mots"] = construire_table(fichier_json)

    return code_source, fichier_json


if __name__ == "__main__":
    main()
