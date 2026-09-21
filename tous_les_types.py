from typing import TypedDict

class Token(TypedDict) :
    colonne: int
    ligne: int
    longueur: int
    type: str
    valeur: str | int | float | None
