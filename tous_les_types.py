from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypedDict, Union
from erreur import erreur

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

    def parse_aide_parametre(self) -> Parametre:
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("declaration_type")
        le_type: str = self.token_courant()["valeur"]
        if self.token_courant()["valeur"] not in LES_TYPES_PRIS :
            self.erreur(f"{self.token_courant()['valeur']} type non pris en charge.")
        self.consommer("mots_cles")

        return Parametre(nom, le_type)

    def parse_parametres(self) -> list[Parametre]:
        self.consommer("PAREN_OUVRANT")
        arguments: list[Parametre] = []
        while(self.token_courant()["type"] != "PAREN_FERMANT") :
            arguments.append(self.parse_aide_parametre())
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

    def parse_bloc_constantes(self) -> list[Declaration]:
        self.consommer("mots_cles", "constante")
        resultats: list[Declaration] = []
        while self.token_courant()["valeur"] == "tableau" or self.token_courant()["type"] == "identifiant" :
            if self.token_courant()["valeur"] == "tableau" :
                resultats.append(self.aide_constante_tableau())
            else :
                resultats.append(self.parse_aide_constante())

        return resultats

    def parse_aide_constante(self) -> DeclarationConstante:
        ligne_debut = self.token_courant()["ligne"]
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("operateurs_affectation")
        valeur: Expression = self.parse_expression()

        if self.token_courant()["ligne"] == ligne_debut:
            self.erreur("chaque ligne ne doit contenir qu'une seule instruction")

        return DeclarationConstante(nom, valeur)

    def aide_constante_tableau(self) -> DeclarationTableau:
        ligne_debut = self.token_courant()["ligne"]
        self.consommer("mots_cles", "tableau")
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("operateurs_affectation")
        les_arguments = self.parse_arguments()

        if self.token_courant()["ligne"] == ligne_debut:
            self.erreur("chaque ligne ne doit contenir qu'une seule instruction")
            
        return DeclarationTableau(nom, None, None, les_arguments)
        

    def parse_bloc_variables(self) -> list[Declaration]:
        self.consommer("mots_cles", "variable")
        resultats: list[Declaration] = []
        while self.token_courant()["valeur"] == "tableau" or self.token_courant()["type"] == "identifiant" :
            if self.token_courant()["valeur"] == "tableau" :
                resultats.append(self.parse_aide_tableau())
            else :
                resultats.extend(self.parse_aide_variable())

        return resultats

    def parse_aide_variable(self) -> list[DeclarationVariable]:
        ligne_debut = self.token_courant()["ligne"]
        noms: list[str] = []
        noms.append(self.token_courant()["valeur"])
        self.consommer("identifiant")
        while self.token_courant()["type"] == "separateur" :
            self.consommer("separateur")
            noms.append(self.token_courant()["valeur"])
            self.consommer("identifiant")
        self.consommer("declaration_type")
        type_: str = self.token_courant()["valeur"]
        if type_ not in LES_TYPES_PRIS :
            self.erreur(f"{type_} non pris en charge dans le langage EVA")
        self.consommer("mots_cles")
        if self.token_courant()["ligne"] == ligne_debut :
            self.erreur("chaque ligne ne doit contenir qu'une seule instruction")

        return [DeclarationVariable(nom, type_) for nom in noms]

    def parse_aide_tableau(self) -> DeclarationTableau : # Tableau 1D et 2D uniquement
        ligne_debut = self.token_courant()["ligne"]
        self.consommer("mots_cles", "tableau")
        nom: str = self.token_courant()["valeur"]
        dimensions: list[Expression] = []
        self.consommer("identifiant")
        self.consommer("PAREN_OUVRANT")
        dimensions.append(self.parse_expression())
        if self.token_courant()["type"] == "separateur" :
            self.consommer("separateur")
            dimensions.append(self.parse_expression())
        self.consommer("PAREN_FERMANT")
        self.consommer("declaration_type")
        type_: str = self.token_courant()["valeur"]
        if type_ not in LES_TYPES_PRIS :
            self.erreur(f"{type_} non pris en charge dans le langage EVA")
        self.consommer("mots_cles")
        if self.token_courant()["ligne"] == ligne_debut :
            self.erreur("chaque ligne ne doit contenir qu'une seule instruction")

        return DeclarationTableau(nom, type_, dimensions)

    def parse_corps(self) -> list[Instruction]:
        self.consommer("mots_cles", "debut")
        retour: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "fin")
        return retour

    def parse_instructions(self) -> list[Instruction]:
        resultats: list[Instruction] = []
        while not self.est_fin_bloc() :
            resultats.append(self.parse_instruction())

        return resultats

    def parse_pour(self) :
        pass

    def parse_tant_que(self) :
        pass

    def parse_retourne(self) :
        pass

    def parse_affectation(self) :
        pass

    def parse_arguments(self) :
        pass

    def parse_instruction(self) -> Instruction : # parse_
        if self.token_courant()["type"] == "identifiant" :
            if self.token_suivant()["type"] == "operateurs_affectation" :
                return self.parse_affectation()
            elif (self.token_suivant()["type"] == "PAREN_OUVRANT") :
                nom: str = self.token_courant()["valeur"]
                self.consommer("identifiant")
                les_arguments = self.parse_arguments()
                if self.token_courant()["type"] == "operateurs_affectation" :
                    self.consommer("operateurs_affectation")
                    retour: Expression = self.parse_expression()
                    return Affectation(Indexation(nom, les_arguments), retour)
                else :
                    return AppelInstruction(nom, les_arguments)
            else :
                self.erreur("Instruction invalide : identifiant tout seul")
        else :
            match self.token_courant()["valeur"] :
                case "ecrire" : return self.parse_ecrire()
                case "lire" : return self.parse_lire()
                case "si" : return self.parse_si()
                case "cas": return self.parse_cas()
                case "pour": return self.parse_pour()
                case "tant que" : return self.parse_tant_que()
                case "repeter" : return self.parse_repeter()
                case "retourne" : return self.parse_retourne()
                _ : self.erreur("voici ce qui était attendu : Identifiant | un mots clé")

    def parse_ecrire(self) :
        pass

    def parse_lire(self) :
        pass
        
    def parse_si(self) :
        pass

    def parse_cas(self) :
        pass

    def parse_repeter(self) :
        pass

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
    
@dataclass
class DeclarationConstante:
    nom: str
    valeur: Expression

@dataclass
class DeclarationTableau:
    nom: str
    type: str | None = None
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
