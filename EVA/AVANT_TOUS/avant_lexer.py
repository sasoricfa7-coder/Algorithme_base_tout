#FICHIER EXTERNE
from UTILS.erreur import aide_remonter, erreur
from UTILS.utils import sans_accents

#IMPORTATION PYTHON
import os
import json
import sys
from pathlib import Path

def verificateur() -> str:
    if len(sys.argv) < 2:
        erreur("Aucun fichier indiqué // No file provided 📁")
    guide: str = sys.argv[1]
    
    # ✅ Convertit en chemin absolu
    nom = os.path.abspath(guide)

    if not os.path.isfile(nom):
        erreur(f"Le fichier {guide} n'existe pas // File {guide} not found 🔍")

    return nom, guide


def charger_code(nom: str) -> str:
    with open(nom, "r", encoding="utf-8") as f:
        return f.read()


def charger_json(nom: str) -> dict:
    with open(nom, "r", encoding="utf-8") as f:
        contenu = json.load(f)
    return contenu


def construire_table(le_json: dict) -> dict[str, tuple[str, str]]:
    # ... (ton code de construction de table reste inchangé)
    normalisation_brute: dict[str, str] = le_json.get("normalisation", {})
    normalisation: dict[str, str] = {
        sans_accents(alias): sans_accents(canonique)
        for alias, canonique in normalisation_brute.items()
    }

    table: dict[str, tuple[str, str]] = {}
    for cle, type_ in (
        ("mots_cles",               "mots_cles"),
        ("operateurs_logiques",     "operateurs_logiques"),
        ("operateurs_arihmetiques", "operateurs_arihmetiques"),
        ("valeur_booleen",          "valeur_booleen"),
    ):
        for mot in le_json[cle]:
            mot_norm = sans_accents(mot)
            canonique = normalisation.get(mot_norm, mot_norm)
            table[mot_norm] = (type_, canonique)

    return table


def main() -> tuple[str, dict]:
    nom, guide = verificateur()
    code_source: str = charger_code(nom)
    
    # ✅ Chemin basé sur l'emplacement du script
    chemin_json = Path(__file__).parent / "langage.json"
    fichier_json: dict = charger_json(chemin_json)

    if code_source.strip() == "":
        erreur(f"{guide} est vide // {nom} is empty 🕳️")

    # ✅ pré-calcul unique
    fichier_json["table_mots"] = construire_table(fichier_json)

    return code_source, fichier_json


if __name__ == "__main__":
    main()
