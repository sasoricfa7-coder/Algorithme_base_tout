from typing import TypedDict

MAX: int = 3  # nombre max de mots pouvant former un mot-clé : "Fin tant que"


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
