from __future__ import annotations
from dataclasses import dataclass, field, is_dataclass, fields
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
#------------ANALYSEUR_SEMANTIQUE-------------------------------------------
@dataclass
class Symbole:
    nom: str
    type: str
    est_constante: bool = False

@dataclass
class TableSymboles:
    pile: list[dict[str, Symbole]] = field(default_factory=list)

    def entrer_portee(self) -> None:
        self.pile.append({})

    def sortir_portee(self) -> None:
        self.pile.pop()

    def declarer(self, nom: str, symbole: Symbole) -> None:
        if nom in self.pile[-1] :
            self.erreur(f"Le symbole '{nom}' est déjà déclaré dans ce bloc 🚫")
        self.pile[-1][nom] = symbole

    def rechercher(self, nom: str) -> Symbole | None :
        for portee in reversed(self.pile):
            if nom in portee:
                return portee[nom]
        return None

    def erreur(self, message="") -> None:
        erreur(message)

@dataclass
class AnalyseurSemantique:
    ast: Algorithme
    tables: TableSymboles = field(default_factory=TableSymboles)

    def visiter_algorithme(self):
        self.tables.entrer_portee()
        self.visiter_fonctions()
        self.visiter_procedures()
        self.visiter_declarations(self.ast.declarations())
        self.visiter_corps()
        self.tables.sortir_portee()

    def visiter_fonctions(self):
        pass
    def visiter_procedures(self):
        pass
    def visiter_declarations(self, declarations):
        for decl in declarations:
            if isinstance(decl, DeclarationVariable) :
                self.tables.declarer(decl.nom, Symbole(decl.nom, decl.type))
            elif isinstance(decl, DeclarationConstante) :
                self.tables.declarer(decl.nom, Symbole(decl.nom, self.type_inferer(decl.valeur), True))
            else :
                if decl.type == None :
                    self.tables.declarer(decl.nom, Symbole(decl.nom, self.type_inferer(decl.valeurs_initiales, True), True))
                else :
                    self.tables.declarer(decl.nom, Symbole(decl.nom, decl.type))
                

                    
    def visiter_corps(self):
        pass

    def type_inferer(self, valeur, est_tableau: bool = False ) :
        if not est_tableau :
            if (len(str(valeur)) == 1) and (not str(valeur).isdigit()) :
                return "caractere"
                # Je suis en reflexion car corriger le parseur rendrait cette méthode inutile
        

















































































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

    def fin_de_ligne(self) -> None:
        """Vérifie que le token courant est sur une autre ligne que le précédent."""
        if self.tokens[self.position - 1]["ligne"] == self.tokens[self.position]["ligne"]:
            self.erreur("Rien ne doit suivre un marqueur de fin de bloc sur la même ligne")


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
        self.consommer("mots_cles", "fonction")
        nom: str = str(self.token_courant()["valeur"])
        self.consommer("identifiant")
        parametre: list[Parametre] = self.parse_parametres()
        self.consommer("declaration_type")
        
        type_retour: str = str(self.token_courant()["valeur"])
        if type_retour not in LES_TYPES_PRIS :
            self.erreur(f"Type de retour '{type_retour}' non pris en charge.")
            
        self.consommer("mots_cles")
        declaration: list[Declaration] = self.parse_declaration()
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
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("operateurs_affectation")
        valeur: Expression = self.parse_expression()

        self.fin_de_ligne()
        return DeclarationConstante(nom, valeur)

    def aide_constante_tableau(self) -> DeclarationTableau:
        self.consommer("mots_cles", "tableau")
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("operateurs_affectation")
        les_arguments = self.parse_arguments()

        self.fin_de_ligne()
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
        
        return [DeclarationVariable(nom, type_) for nom in noms]

    def parse_aide_tableau(self) -> DeclarationTableau : # Tableau 1D et 2D uniquement
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
        
        return DeclarationTableau(nom, type_, dimensions)

    def parse_instructions(self) -> list[Instruction]:
        resultats: list[Instruction] = []
        while not self.est_fin_bloc() :
            resultats.append(self.parse_instruction())
            self.fin_de_ligne()
        return resultats

    def parse_corps(self) : # Lui ne gère que les cas ou on est entourer debut ... fin
        self.consommer("mots_cles", "debut")
        corps: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "fin")
        return corps

    def parse_affectation(self) -> Affectation:
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("operateurs_affectation")
        retour: Expression = self.parse_expression()
        return Affectation(Identifiant(nom), retour)

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
                case _ : self.erreur("voici ce qui était attendu : Identifiant | un mots clé")

    def parse_ecrire(self) -> Ecrire:
        self.consommer("mots_cles", "ecrire")
        return Ecrire(self.parse_arguments())

    def parse_cible(self) -> Identifiant | Indexation:
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        if self.token_courant()["type"] == "PAREN_OUVRANT" :
            indices = self.parse_arguments()
            return Indexation(nom, indices)
        return Identifiant(nom)

    def parse_lire(self) -> Lire:
        self.consommer("mots_cles", "lire")
        self.consommer("PAREN_OUVRANT")
        cibles: list[Identifiant | Indexation] = []
        cibles.append(self.parse_cible())
        while self.token_courant()["type"] == "separateur" :
            self.consommer("separateur")
            cibles.append(self.parse_cible())
        self.consommer("PAREN_FERMANT")
        return Lire(cibles)
        
    def parse_si(self) -> Si:
        self.consommer("mots_cles", "si")
        condition: Expression = self.parse_expression()
        self.consommer("mots_cles", "alors")
        alors: list[Instruction] = self.parse_instructions()
        sinon: list[Instruction] = []
        if self.token_courant()["valeur"] == "sinon" :
            self.consommer("mots_cles", "sinon")
            sinon = self.parse_instructions()

        self.consommer("mots_cles", "fin si")
        return Si(condition, alors, sinon)

    def parse_branche_cas(self) -> BrancheCas:
        valeur: Expression = self.parse_expression()
        self.consommer("declaration_type")
        if self.token_courant()["valeur"] in ("si", "cas", "pour", "tant que", "repeter") :
            self.erreur("Un bloc ne peut pas tenir sur une ligne dans un Cas : entourer le dans un debut ... fin")

        corps: list[Instruction] = []
        if self.token_courant()["valeur"] == "debut" :
            corps = self.parse_corps()
        else :
            corps = [self.parse_instruction()]
            self.fin_de_ligne()
        return BrancheCas(valeur, corps)

    def parse_cas(self) -> Cas:
        self.consommer("mots_cles", "cas")
        nom: Identifiant | Indexation = self.parse_cible()
        self.consommer("mots_cles", "vaut")
        les_branches: list[BrancheCas] = []
        while self.token_courant()["valeur"] not in ("fin cas", "sinon") :
            les_branches.append(self.parse_branche_cas())
            
        if self.token_courant()["valeur"] != "sinon" :
            self.erreur("Le Sinon est obligatoire dans Cas")
            
        self.consommer("mots_cles", "sinon")
        self.consommer("declaration_type")
        sinon: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "fin cas")
        return Cas(nom, les_branches, sinon)

    def parse_pour(self) -> Pour:
        self.consommer("mots_cles", "pour")
        indice: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("operateurs_affectation")
        debut: Expression = self.parse_expression()
        self.consommer("mots_cles", "a")
        fin: Expression = self.parse_expression()
        self.consommer("mots_cles", "pas")
        pas: Expression = self.parse_expression()
        self.consommer("mots_cles", "faire")
        corps: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "fin pour")

        return Pour(Identifiant(indice), debut, fin, pas, corps)

    def parse_tant_que(self) -> TantQue:
        self.consommer("mots_cles", "tant que")
        condition: Expression = self.parse_expression()
        self.consommer("mots_cles","faire")
        corps: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "fin tant que")
        return TantQue(condition, corps)

    def parse_repeter(self) -> Repeter:
        self.consommer("mots_cles", "repeter")
        corps: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "jusqu'a")
        condition: Expression = self.parse_expression()
        return Repeter(corps, condition)

    def parse_retourne(self) -> Retourne:
        self.consommer("mots_cles", "retourne")
        valeur: Expression = self.parse_expression()
        return Retourne(valeur)

    def parse_arguments(self) -> list[Expression]:
        self.consommer("PAREN_OUVRANT")
        les_arguments: list[Expression] = []
        les_arguments.append(self.parse_expression())
        while self.token_courant()["type"] == "separateur" :
            self.consommer("separateur")
            les_arguments.append(self.parse_expression())

        self.consommer("PAREN_FERMANT")
        return les_arguments

    def parse_expression(self) -> Expression:
        return self.parse_ou_expr()
    def parse_ou_expr(self) :
        gauche: Expression = self.parse_et_expr()
        
        while self.token_courant()["valeur"] == "ou" :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_logiques", "ou") # je veux rester coherent
            droite: Expression = self.parse_et_expr()
            gauche = OperationBinaire(operateur, gauche, droite)

        return gauche

    def parse_et_expr(self) -> Expression:
        gauche: Expression = self.parse_non_expr()
        
        while self.token_courant()["valeur"] == "et" :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_logiques", "et") # je veux rester coherent
            droite: Expression = self.parse_non_expr()
            gauche = OperationBinaire(operateur, gauche, droite)

        return gauche

    def parse_non_expr(self) -> Expression:
        if self.token_courant()["valeur"] == "non" :
            self.consommer("operateurs_logiques", "non")
            operande: Expression = self.parse_non_expr()
            return OperationUnaire("non", operande)
        return self.parse_comparaison()

    def parse_comparaison(self) -> Expression:
        gauche: Expression = self.parse_additif()
        if self.token_courant()["type"] == "operateurs_comparaison" :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_comparaison")
            droite: Expression = self.parse_additif()
            gauche = OperationBinaire(operateur, gauche, droite)
        return gauche

    def parse_additif(self) -> Expression:
        gauche: Expression = self.parse_multiplicatif()
        while self.token_courant()["valeur"] in ("+", "-") :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_arihmetiques")
            droite: Expression = self.parse_multiplicatif()
            gauche = OperationBinaire(operateur, gauche, droite)
        return gauche
        
    def parse_multiplicatif(self) -> Expression:
        gauche: Expression = self.parse_puissance()
        while self.token_courant()["valeur"] in ("*", "/", "mod", "div") :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_arihmetiques")
            droite: Expression = self.parse_puissance()
            gauche = OperationBinaire(operateur, gauche, droite)
        return gauche
        
    def parse_puissance(self) -> Expression:
        gauche: Expression = self.parse_unaire()
        if self.token_courant()["valeur"] == "^" :
            operateur: str = str(self.token_courant()["valeur"])
            self.consommer("operateurs_arihmetiques", "^")
            droite: Expression = self.parse_puissance()  # Récursion à droite
            return OperationBinaire(operateur, gauche, droite)
        return gauche
        
    def parse_unaire(self) -> Expression:
        if self.token_courant()["valeur"] in ("+", "-") :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_arihmetiques")
            operande: Expression = self.parse_unaire()
            return OperationUnaire(operateur, operande)
        return self.parse_primaire()

    def parse_primaire(self) -> Expression:
        token: Token = self.token_courant()
        type_token: str = token["type"]
        valeur_token = token["valeur"]

        if type_token == "NOMBRE" :
            self.consommer("NOMBRE")
            return Nombre(valeur_token)

        elif type_token == "CHAINE_CARACTERE" :
            self.consommer("CHAINE_CARACTERE")
            return ChaineCaractere(str(valeur_token))

        elif type_token == "CARACTERE" :
            self.consommer("CARACTERE")
            return Caractere(str(valeur_token))

        elif type_token == "valeur_booleen" :
            self.consommer("valeur_booleen")
            return Booleen(valeur_token == "vrai")

        elif type_token == "identifiant" :
            nom: str = str(valeur_token)
            self.consommer("identifiant")

            if self.token_courant()["type"] == "PAREN_OUVRANT" :
                les_arguments: list[Expression] = self.parse_arguments()
                return AppelFonction(nom, les_arguments)

            return Identifiant(nom)

        elif type_token == "PAREN_OUVRANT" :
            self.consommer("PAREN_OUVRANT")
            expr: Expression = self.parse_expression()
            self.consommer("PAREN_FERMANT")
            return expr
        else :
            self.erreur(f"Expression inattendue : token '{type_token}' ({valeur_token})")

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
    type: str | None = None

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
    expression: Identifiant | Indexation
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
    pas: Expression
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


def afficher_ast(node, indent="", last=True):
    """Affiche un AST fait de dataclasses sous forme d'arbre ASCII."""
    prefix = "└── " if last else "├── "
    child_indent = indent + ("    " if last else "│   ")

    if is_dataclass(node):
        print(f"{indent}{prefix}\033[1;34m{node.__class__.__name__}\033[0m")
        field_list = fields(node)
        for i, field in enumerate(field_list):
            val = getattr(node, field.name)
            is_last_field = (i == len(field_list) - 1)
            field_prefix = "└── " if is_last_field else "├── "
            sub_child_indent = child_indent + ("    " if is_last_field else "│   ")
            
            print(f"{child_indent}{field_prefix}\033[33m{field.name}\033[0m:")
            
            if isinstance(val, list):
                if not val:
                    print(f"{sub_child_indent}└── []")
                else:
                    for j, item in enumerate(val):
                        afficher_ast(item, sub_child_indent, j == len(val) - 1)
            elif is_dataclass(val):
                afficher_ast(val, sub_child_indent, True)
            else:
                print(f"{sub_child_indent}└── \033[32m{repr(val)}\033[0m")

    elif isinstance(node, list):
        for i, item in enumerate(node):
            afficher_ast(item, indent, i == len(node) - 1)
    else:
        print(f"{indent}{prefix}\033[32m{repr(node)}\033[0m")


Expression = Union[Nombre, ChaineCaractere, Caractere, Booleen, Identifiant,
                   OperationBinaire, OperationUnaire, AppelFonction, Indexation]

Instruction = Union[Affectation, Ecrire, Lire, Si, Cas, Pour, TantQue,
                    Repeter, Retourne, AppelInstruction]

Declaration = Union[DeclarationVariable, DeclarationConstante, DeclarationTableau]

Noeud = Union[Expression, Instruction, Declaration] # La pour tout
