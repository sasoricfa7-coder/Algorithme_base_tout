from __future__ import annotations
from environnement import Environnement
from erreur import erreur
from tous_les_types import (
    Algorithme, Fonction, Procedure, DeclarationVariable, DeclarationConstante,
    DeclarationTableau, Affectation, Ecrire, Lire, Si, Cas, Pour, TantQue, Repeter,
    Retourne, AppelInstruction, Nombre, ChaineCaractere, Caractere, Booleen,
    Identifiant, OperationBinaire, OperationUnaire, AppelFonction, Indexation,
    Instruction
)

class SignalRetour(Exception):
    def __init__(self, valeur):
        self.valeur = valeur
        super().__init__(str(valeur))

class Interpreteur:
    def __init__(self, env_global=None, env_courant=env_global, fonctions={}, procedures={}):
        self.env_global = Environnement() if env_global is None else env_global
        self.env_courant = env_courant
        self.fonctions: dict[str, Fonction] = fonctions
        self. procedures: dict[str, Procedure] = procedures

    def interpreter(self, ast: Algorithme) -> None:
        for fonction in ast.fonctions:
            self.fonctions[fonction.nom] = fonction

        for procedure in ast.procedures:
            self.procedures[procedure.nom] = procedure

        for decl in ast.declarations:
            self.executer_instruction(decl)

        for inst in ast.corps:
            self.executer_instruction(inst)

    def definir(self, nom: str, valeur) -> None:
        if valeur in ("vrai", "faux"):
            valeur = False if valeur=="faux" else True
        self.env_courant.definir(nom, valeur)

    def ecrire(self, inst) -> None:
        for arg in inst.arguments:
            print(self.evaluer_expression(arg), end="")
        print()

    def evaluer_expression(self, un_cas):
        if isinstance(un_cas, Nombre) or isinstance(un_cas, ChaineCaractere) or isinstance(un_cas, Caractere) or isinstance(un_cas, Booleen):
            if isinstance(un_cas, Booleen):
                retour = False if un_cas.valeur=="faux" else True
                return retour
            return un_cas.valeur
        if isinstance(un_cas, Identifiant):
            return self.env_courant.obtenir(un_cas.nom)
        if isinstance(un_cas, OperationBinaire):
            gauche = self.evaluer_expression(un_cas.gauche)
            droite = self.evaluer_expression(un_cas.droite)
            return self.operation_binaire(gauche, droite, un_cas.operateur)
        if isinstance(un_cas, OperationUnaire):
            operande = self.evaluer_expression(un_cas.operande)
            if un_cas.operateur == "-":
                return -1 * operande
            return not operande
        if isinstance(un_cas, AppelFonction):
            
        if isinstance(un_cas, Indexation):
            pass

    def operation_binaire(self, gauche, droite, operateur):
        def verifie_zero(droite) -> None:
            if droite == 0 or droite == 0.0:
                self.erreur("Division par zero detecter à l'execution")
        match operateur:
            case "+": resultat = gauche + droite
            case "-": resultat = gauche - droite
            case "*": resultat = gauche * droite
            case "/": 
                verifie_zero(droite)
                resultat = gauche / droite
            case "^": resultat = gauche ** droite
            case "div": 
                verifie_zero(droite)
                resultat = gauche // droite
            case "mod": 
                verifie_zero(droite)
                resultat = gauche % droite
            case "=": resultat = gauche == droite
            case "<": resultat = gauche < droite
            case "<=": resultat = gauche <= droite
            case ">": resultat = gauche > droite
            case ">=": resultat = gauche >= droite
            case "<>": resultat = gauche != droite
            case "et": resultat = gauche and droite
            case "ou": resultat = gauche or droite
        return resultat

    def executer_instruction(self, inst: Instruction) -> None:
        if isinstance(inst, DeclarationConstante):
            self.definir(inst.nom, inst.valeur)
        elif isinstance(inst, DeclarationVariable):
            match inst.type:
                case "entier": valeur = 0
                case "reel": valeur = 0.0
                case "chaine": valeur = ""
                case "booleen": valeur = "vrai"
                case _ "caractere": valeur = ''
            self.definir(inst.nom, valeur)
        elif isinstance(inst, Affectation):
            
        elif isinstance(inst, Ecrire): 
            self.ecrire(inst)
                                

            print()
        
    
