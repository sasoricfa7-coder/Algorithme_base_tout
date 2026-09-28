from __future__ import annotations
from environnement import Environnement
from dataclasses import dataclass, field
from erreur import erreur
from tous_les_types import (
    Algorithme, Fonction, Procedure, DeclarationVariable, DeclarationConstante,
    DeclarationTableau, Affectation, Ecrire, Lire, Si, Cas, Pour, TantQue, Repeter,
    Retourne, AppelInstruction, Nombre, ChaineCaractere, Caractere, Booleen,
    Identifiant, OperationBinaire, OperationUnaire, AppelFonction, Indexation
)

class SignalRetour(Exception):
    def __init__(self, valeur):
        self.valeur = valeur
        super().__init__(str(valeur))

@dataclass
class Interpreteur:
    env_global = Environnement()
    env_courant = env_global
    fonctions: dict[str, Fonction] = field(default_factory=dict)
    procedures: dict[str, Procedure] = field(default_factory=dict)

    def interpreter(self, ast: Algorithme) -> None:
        for fonction in ast.fonctions:
            self.fonctions[fonction.nom] = fonction
        for procedure in ast.procedures:
            self.procedures[procedure.nom] = procedure
        
        
    
