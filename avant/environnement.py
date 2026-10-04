from __future__ import annotations
from dataclasses import dataclass, field, is_dataclass, fields
from erreur import erreur
from typing import Any

@dataclass
class Environnement:
    dict_valeur: dict = field(default_factory=dict)
    parent: Environnement | None = None

    def erreur(self, message: str=""):
        message = f"Interpréteur → {message}"
        erreur(message)

    def definir(self, nom: str, valeur) -> None:
        self.dict_valeur[nom] = valeur

    def obtenir(self, nom: str) -> Any:
        if nom in self.dict_valeur:
            return self.dict_valeur[nom]

        if self.parent is not None:
            return self.parent.obtenir(nom)
        self.erreur(f"{nom} inconnu")

    def modifier(self, nom: str, valeur) -> None:
        if nom in self.dict_valeur:
            self.dict_valeur[nom] = valeur
            return

        if self.parent is not None:
            self.parent.modifier(nom, valeur)
            return
        self.erreur(f"{nom} valeur inconnue")
