from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypedDict, Union
from erreur import erreur
from utils import sans_accents

MOTS_FIN_BLOC: tuple[str, ...] = (
    "fin", "fin si", "fin cas", "fin pour", "fin tant que",
    "sinon", "jusqu'a",
)

#------------PARSEUR-------------------------------------------
@dataclass
class Parseur:
    tokens: list[Token]
    position: int

    def token_courant(self) :
        return self.tokens[position]

    def token_suivant(self) :
        return self.tokens[position + 1]

    def avancer(self) :
        self.position += 1

    def verifier(self, type_: str, valeur = None) :
        if self.tokens[position].type != type_ :
            erreur(f"type : {type_} : c'est ce qui était attendu.", self.tokens[position].ligne)
        elif (valeur != None) and (self.tokens[position].valeur != valeur) :
            erreur(f"valeur : {valeur} : c'est ce qui était attendu.", self.tokens[position].ligne)

    def consommer(self, type_, valeur=None) :
        self.verifier(type_, valeur)
        self.avancer()

    def est_fin_bloc(self) :
        if self.tokens[position].valeur in MOTS_FIN_BLOC :
            return True
        return False

    def erreur(self, message) :
        erreur(message, self.tokens[position].ligne)


    def parse_programme(self) :
        self.parse_algorithme()

    def parse_algorithme(self) :
        if self.tokens[position].valeur




















        
    
#------------PARSEUR-------------------------------------------

MAX: int = 3 # nombre max de mots pouvant former un mot-clé : "Fin tant que"

@dataclass
class Algorithme:
    nom: str
    fonctions: list[Fonction]
    procedures: list[Procedure]
    declarations: list[Declaration] # ici je me dis c'est mieux plutard une class Declaration avec les types
    corps: list[Instruction]

@dataclass
class Fonction:
    nom: str
    parametres: list[Parametre]
    type_retour: str
    declarations: list[Declaration]
    corps: list[Instruction]

@dataclass
class Procedure:
    nom: str
    parametres: list[Parametre]
    declarations: list[Declaration]
    corps: list[Instruction]

@dataclass
class Parametre:
    nom: str
    type: str

@dataclass
class DeclarationVariable:
    nom: str
    type: str
    valeur_initiale: Expression | None = None
    
@dataclass
class DeclarationConstante:
    nom: str
    valeur: Expression
    type: str | None = None

@dataclass
class DeclarationTableau:
    nom: str
    type: str
    dimensions: list[Expression] | None = None
    valeurs_initiales: list[Expression] | None = None

@dataclass
class Affectation:
    cible: Identifiant | Indexation
    valeur: Expression

@dataclass
class Ecrire:
    arguments: list[Expression]

@dataclass
class Lire:
    cibles: list[Identifiant | Indexation]

@dataclass
class Si:
    condition: Expression
    alors: list[Instruction]
    sinon: list[Instruction] = field(default_factory=list)

@dataclass
class Cas:
    expression: Expression
    branches: list[BrancheCas]
    sinon: list[Instruction] = field(default_factory=list)

@dataclass
class BrancheCas:
    valeur: Expression
    instructions: list[Instruction]

@dataclass
class Pour:
    indice: Identifiant
    debut: Expression
    fin: Expression
    pas: Expression | None = None
    corps: list[Instruction]

@dataclass
class TantQue:
    condition: Expression
    corps: list[Instruction]

@dataclass
class Repeter:
    corps: list[Instruction]
    condition: Expression

@dataclass
class Retourne:
    valeur: Expression

@dataclass
class AppelInstruction:
    nom: str
    arguments: list[Expression]

@dataclass
class Nombre:
    valeur: int | float

@dataclass
class ChaineCaractere:
    valeur: str

@dataclass
class Caractere:
    valeur: str

@dataclass
class Booleen:
    valeur: bool

@dataclass
class Identifiant:
    nom: str

@dataclass
class OperationBinaire:
    operateur: str #(+, -, *, /, ^, div, mod, =, <, >, <=, >=, <>, et, ou)
    gauche: Expression
    droite: Expression

@dataclass
class OperationUnaire:
    operateur: str # (non, - pour négation)
    operande: Expression

@dataclass
class AppelFonction:
    nom: str
    arguments: list[Expression]

@dataclass
class Indexation:
    nom: str
    indices: list[Expression]




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
    table_mots: dict[str, str]   # ✅ ajouté

Expression = Union[Nombre, ChaineCaractere, Caractere, Booleen, Identifiant,
                   OperationBinaire, OperationUnaire, AppelFonction, Indexation]

Instruction = Union[Affectation, Ecrire, Lire, Si, Cas, Pour, TantQue,
                    Repeter, Retourne, AppelInstruction]

Declaration = Union[DeclarationVariable, DeclarationConstante, DeclarationTableau]

Noeud = Union[Expression, Instruction, Declaration] # La pour tout
