from typing import TypedDict

class Token(TypedDict):
    ligne: int
    type: str
    valeur: str | int | float | None

class Langage(TypedDict):
        mots_cles: list[str]
        operateurs_logiques: list[str]
        operateurs_comparaison: list[str]
        operateurs_arihmetiques: list[str]
        valeur_booleen: list[str]
        operateurs_affectation: list[str]
        commentaire: list[str]
        separateur: list[str]
        declaration_type: list[str]
        normalisation: dict[str, str]                 # ✅ ajouté
        table_mots: dict[str, tuple[str, str]]        # ✅ type mis à jour
