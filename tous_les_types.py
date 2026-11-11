from __future__ import annotations
from dataclasses import dataclass, field, is_dataclass, fields
from typing import TypedDict, Union

MOTS_FIN_BLOC: tuple[str, ...] = (
    "fin", "fin si", "fin cas", "fin pour", "fin tant que",
    "sinon", "jusqu'a",
)
LES_TYPES_PRIS: tuple[str, ...] = (
    "entier",
    "reel",
    "caractere",
    "chaine",
    "booleen",
)

MAX: int = 3 # nombre max de mots pouvant former un mot-clé : "Fin tant que"

@dataclass
class Algorithme:
    nom: str
    fonctions: list[Fonction]
    procedures: list[Procedure]
    declarations: list[Declaration]
    corps: list[Instruction]
    ligne: int = -1

@dataclass
class Fonction:
    nom: str
    parametres: list[Parametre]
    type_retour: str
    declarations: list[Declaration]
    corps: list[Instruction]
    retour_est_tableau: bool = False
    ligne: int = -1

@dataclass
class Procedure:
    nom: str
    parametres: list[Parametre]
    declarations: list[Declaration]
    corps: list[Instruction]
    ligne: int = -1

@dataclass
class Parametre:
    nom: str
    type: str
    est_tableau: bool = False
    ligne: int = -1

@dataclass
class DeclarationVariable:
    nom: str
    type: str
    ligne: int = -1
    
@dataclass
class DeclarationConstante:
    nom: str
    valeur: Expression
    type: str | None = None
    ligne: int = -1

@dataclass
class DeclarationTableau:
    nom: str
    type: str | None = None
    dimensions: list[Expression] | None = None
    valeurs_initiales: list[Expression] | None = None
    ligne: int = -1

@dataclass
class Affectation:
    cible: Identifiant | Indexation
    valeur: Expression
    ligne: int = -1

@dataclass
class Ecrire:
    arguments: list[Expression]
    ligne: int = -1

@dataclass
class Lire:
    cibles: list[Identifiant | Indexation]
    ligne: int = -1

@dataclass
class Si:
    condition: Expression
    alors: list[Instruction]
    sinon: list[Instruction] = field(default_factory=list)
    ligne: int = -1

@dataclass
class Cas:
    expression: Identifiant | Indexation
    branches: list[BrancheCas]
    sinon: list[Instruction] = field(default_factory=list)
    ligne: int = -1

@dataclass
class BrancheCas:
    valeur: Expression
    instructions: list[Instruction]
    ligne: int = -1

@dataclass
class Pour:
    indice: Identifiant
    debut: Expression
    fin: Expression
    pas: Expression
    corps: list[Instruction]
    ligne: int = -1

@dataclass
class TantQue:
    condition: Expression
    corps: list[Instruction]
    ligne: int = -1

@dataclass
class Repeter:
    corps: list[Instruction]
    condition: Expression
    ligne: int = -1

@dataclass
class Retourne:
    valeur: Expression
    ligne: int = -1

@dataclass
class AppelInstruction:
    nom: str
    arguments: list[Expression]
    ligne: int = -1

@dataclass
class Nombre:
    valeur: int | float
    ligne: int = -1

@dataclass
class ChaineCaractere:
    valeur: str
    ligne: int = -1

@dataclass
class Caractere:
    valeur: str
    ligne: int = -1

@dataclass
class Booleen:
    valeur: bool
    ligne: int = -1

@dataclass
class Identifiant:
    nom: str
    ligne: int = -1

@dataclass
class OperationBinaire:
    operateur: str #(+, -, *, /, ^, div, mod, =, <, >, <=, >=, <>, et, ou)
    gauche: Expression
    droite: Expression
    ligne: int = -1

@dataclass
class OperationUnaire:
    operateur: str # (non, - pour négation)
    operande: Expression
    ligne: int = -1

@dataclass
class AppelFonction:
    nom: str
    arguments: list[Expression]
    ligne: int = -1

@dataclass
class Indexation:
    nom: str
    indices: list[Expression]
    ligne: int = -1

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

Expression = Union[Nombre, ChaineCaractere, Caractere, Booleen, Identifiant,
                   OperationBinaire, OperationUnaire, AppelFonction, Indexation]

Instruction = Union[Affectation, Ecrire, Lire, Si, Cas, Pour, TantQue,
                    Repeter, Retourne, AppelInstruction]

Declaration = Union[DeclarationVariable, DeclarationConstante, DeclarationTableau]

Noeud = Union[Expression, Instruction, Declaration] # La pour tout
