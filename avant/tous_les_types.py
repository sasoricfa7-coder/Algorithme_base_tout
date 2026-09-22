from typing import TypedDict

MAX: int = 3 # ici c'est le nombre de mot le plus grand pouvant former un mot clé : Tant que
class Token(TypedDict) :
    colonne: int
    ligne: int
    longueur: int
    type: str
    valeur: str | int | float | None

class Langage(TypedDict) :
    mots_cles_simple: list[str]
    les_mots_ambigu: list[str]
    operateurs_logiques: list[str]
    operateurs_comparaison: list[str]
    operateurs_arihmetiques: list[str]
    valeur_booleen: list[str]
    operateurs_affectation: list[str]
    commentaire: list[str]
    autres: list[str]
