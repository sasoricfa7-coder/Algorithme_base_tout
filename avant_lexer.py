import json
import sys
from erreur import gestion as erreur
import os

def verificateur() -> str:
    if len(sys.argv) < 2 :
        erreur("Aucun fichier indiquer.")
    nom: str = sys.argv[1]

    if not os.path.isfile(nom) :
        erreur(f"Le fichier {nom} n'existe pas.")

    return nom

def charger_code(nom: str) -> str :
    with open(nom, "r", encoding="utf-8") as f :
        return f.read()
        


def charger_json(nom: str) -> dict:
    with open(nom, "r", encoding="utf-8") as f :
        contenu = json.load(f)
    return contenu

def main() :
    nom: str = verificateur()
    code_source: str = charger_code(nom)
    fichier_json: dict[str , str] = charger_json("langage.json")

    if code_source.strip() == "":
        erreur(f"{nom} est vide")
    
    return code_source, fichier_json

    
if __name__=="__main__" :
    main()
