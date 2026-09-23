from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypedDict, Union
from erreur import erreur

MOTS_FIN_BLOC: tuple[str, ...] = (
    "fin", "fin si", "fin cas", "fin pour", "fin tant que",
    "sinon", "jusqu'a",
)

#------------PARSEUR-------------------------------------------
class Parseur:
    def __init__(self, tokens: list[Token]) -> None :
        self.tokens: list[Token] = tokens
        self.position: int = 0

    def token_courant(self) -> Token:
        return self.tokens[self.position]

    def token_suivant(self) -> Token:
        if self.position + 1 >= len(self.tokens) :
            self.erreur("Fin de fichier inattendue // Unexpected end of file")
        return self.tokens[self.position + 1]

    def avancer(self) -> None:
        self.position += 1

    def verifier(self, type_: str, valeur = None) -> None:
        if self.tokens[self.position]["type"] != type_ :
            self.erreur(f"type : {type_} : c'est ce qui était attendu.")
        elif (valeur != None) and (self.tokens[self.position]["valeur"] != valeur) :
            self.erreur(f"valeur : {valeur} : c'est ce qui était attendu.")

    def consommer(self, type_, valeur=None) -> None:
        self.verifier(type_, valeur)
        self.avancer()

    def est_fin_bloc(self) -> bool:
        if self.tokens[self.position]["valeur"] in MOTS_FIN_BLOC :
            return True
        return False

    def erreur(self, message) -> None:
        erreur(message, self.tokens[self.position]["ligne"])


    def parse_programme(self) -> Algorithme:
        return self.parse_algorithme()

    def parse_algorithme(self) -> Algorithme:
        self.consommer("mots_cles", "algorithme")
        index_nom: int = self.position
        self.consommer("identifiant")
        # Les differents blocs pour recevoir les retours et former l'AST
        Fonction_bloc: list[Fonction] = []
        Procedure_bloc: list[Procedure] = []
        # Fin des blocs
        while (self.tokens[self.position]["valeur"] in ("fonction", "procedure")) :
            if self.tokens[self.position]["valeur"] == "fonction" :
                Fonction_bloc.append(self.parse_fonction())
            else :
                Procedure_bloc.append(self.parse_procedure())

        declaration = self.parse_declaration()
        corps_complet: list[Instruction] = self.parse_corps()

        return Algorithme(self.tokens[index_nom]["valeur"], Fonction_bloc, Procedure_bloc, declaration, corps_complet )

    def parse_fonction(self) -> Fonction:
        self.consommer( "mots_cles","fonction")
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        parametre: list[Parametre] = self.parse_parametres()
        self.consommer("declaration_type")
        type_retour: str = self.token_courant()["valeur"]
        self.consommer("mots_cles")
        declaration: Declaration = self.parse_declaration()
        corps_complet: list[Instruction] = self.parse_corps()

        return Fonction(nom, parametre, type_retour, declaration, corps_complet)

    def parse_procedure(self) -> Procedure:
        self.consommer( "mots_cles","procedure")
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        parametre: list[Parametre] = self.parse_parametres()
        declaration: Declaration = self.parse_declaration()
        corps_complet: list[Instruction] = self.parse_corps()

        return Procedure(nom, parametre, declaration, corps_complet)

    def parse_type(self) -> Parametre:
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("declaration_type")
        type: str = self.token_courant()["valeur"]
        if self.token_courant()["valeur"] not in ("entier", "reel", "caractere", "chaine", "booleen") :
            self.erreur(f"{self.token_courant()['valeur']} type non pris en charge.")
        self.consommer("mots_cles")

        return Parametre(nom, type)

    def parse_parametres(self) -> list[Parametre]:
        self.consommer("PAREN_OUVRANT")
        arguments: list[Parametre] = []
        while(self.token_courant()["type"] != "PAREN_FERMANT") :
            arguments.append(self.parse_type())
            if self.token_courant()["type"] == "separateur" :
                self.consommer("separateur")

        self.consommer("PAREN_FERMANT")

        return arguments
        

    def parse_declaration(self) -> list[Declaration]:
        Variable_bloc: list[DeclarationVariable] = []
        Constante_bloc: list[DeclarationConstante] = []
        
        vus: set[str] = set()
        while self.token_courant()["valeur"] in ("variable", "constante") :
            mot = self.token_courant()["valeur"]
            if mot in vus :
                self.erreur(f'Bloc "{mot}" déjà déclaré // "{mot}" block already declared 🚫')    
            vus.add(mot)
            if mot == "variable" :
                Variable_bloc += self.parse_bloc_variables()
            else :
                Constante_bloc += self.parse_bloc_constantes()
        return Variable_bloc + Constante_bloc

    def parse_bloc_variables(self) list[Declaration] :
        self.consommer("mots_cles", "variable")
        

#------------PARSEUR-------------------------------------------

MAX: int = 3 # nombre max de mots pouvant former un mot-clé : "Fin tant que"

@dataclass
class Algorithme:
    nom: str
    fonctions: list[Fonction]
    procedures: list[Procedure]
    declarations: list[Declaration]
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
        normalisation: dict[str, str]                 # ✅ ajouté
        table_mots: dict[str, tuple[str, str]]        # ✅ type mis à jour



Expression = Union[Nombre, ChaineCaractere, Caractere, Booleen, Identifiant,
                   OperationBinaire, OperationUnaire, AppelFonction, Indexation]

Instruction = Union[Affectation, Ecrire, Lire, Si, Cas, Pour, TantQue,
                    Repeter, Retourne, AppelInstruction]

Declaration = Union[DeclarationVariable, DeclarationConstante, DeclarationTableau]

Noeud = Union[Expression, Instruction, Declaration] # La pour tout
