from __future__ import annotations
from environnement import Environnement
from dataclasses import dataclass, field
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

        for decl in ast.declarations:
            self.executer_instruction(decl)

        for inst in ast.corps:
            self.executer_instruction(inst)

    def definir(self, nom: str, valeur) -> None:
        if valeur in ("vrai", "faux"):
            valeur = False if valeur=="faux" else True
        self.env_courant.definir(nom, valeur)

    def ecrire(self, arg) -> None:
        print(arg, end="")

    def aide_operation_binaire(self, un_cas):
        if isinstance(un_cas, Nombre) or isinstance(un_cas, ChaineCaractere) or isinstance(un_cas, Caractere) or isinstance(un_cas, Booleen):
            if isinstance(un_cas, Booleen):
                retour = False if un_cas.valeur=="faux" else True
                return retour
            return un_cas.valeur
        if isinstance(un_cas, Identifiant):
            return self.env_courant.obtenir(un_cas.nom)
        if isinstance(un_cas, OperationBinaire):
            return self.aide_operation_binaire(un_cas)
        if isinstance(un_cas, OperationUnaire):
            pass # je me dis même que ce cas est impossible.
        if isinstance(un_cas, AppelFonction):
            pass
        if isinstance(un_cas, Indexation):
            pass

    def operation_binaire(self, gauche, droite, operateur):
        gauche = self.aide_operation_binaire(gauche)
        droite = self.aide_operation_binaire(droite)
        match operateur:
            case "+": resultat = gauche + droite
            case "-": resultat = gauche - droite
            case "*": resultat = gauche * droite
            case "/": resultat = gauche / droite
            case "^": resultat = gauche ** droite
            case "div": resultat = gauche // droite
            case "mod": resultat = gauche % droite
            case "=": resultat = gauche == droite
            case "<": resultat = gauche < droite
            case "<=": resultat = gauche <= droite
            case ">": resultat = gauche > droite
            case ">=": resultat = gauche >= droite
            case "<>": resultat = gauche != droite
            case "et": resultat = gauche and droite
            case "ou": resultat = gauche or droite

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
            if isinstance(inst.cible, Identifiant):
                self.definir(inst.cible.nom, inst.valeur)
            else:
                pass # je ne sais comment faire ca
        elif isinstance(inst, Ecrire):
            for arg in inst.arguments:
                if isinstance(arg, Identifiant):
                    self.ecrire(self.env_courant.obtenir(arg.nom))
                elif isinstance(arg, OperationBinaire):
                    

            print()
        
    
