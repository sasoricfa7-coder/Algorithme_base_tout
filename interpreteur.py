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
    def __init__(self, env_global=None, env_courant=None, fonctions={}, procedures={}):
        self.env_global = Environnement() if env_global is None else env_global
        self.env_courant = self.env_global if env_courant is None else env_courant
        self.fonctions: dict[str, Fonction] = fonctions
        self.procedures: dict[str, Procedure] = procedures  
        self.tout_type: dict[str, str] = {}

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

    def formater(self, valeur: int | float) -> int | float:
        return f"{valeur:_}"

    def ecrire(self, inst) -> None:
        for arg in inst.arguments:
            valeur = self.evaluer_expression(arg)
            if isinstance(valeur, (int, float)):
                valeur = self.formater(valeur)
            print(valeur, end="")
        print()

    def evaluer_expression(self, un_cas):
        if isinstance(un_cas, (Nombre, ChaineCaractere, Caractere, Booleen)):
            if isinstance(un_cas, Booleen):
                return False if un_cas.valeur == "faux" or un_cas.valeur is False else True
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
                return -operande
            elif un_cas.operateur == "+":
                return operande
            elif un_cas.operateur == "non":
                return not operande
            return not operande

        if isinstance(un_cas, AppelFonction):
            if un_cas.nom == "racine":
                if len(un_cas.arguments) != 1:
                    erreur("La fonction 'racine' prend exactement un argument.")
                valeur = self.evaluer_expression(un_cas.arguments[0])
                if not isinstance(valeur, (int, float)):
                    erreur("L'argument de 'racine' doit être un nombre.")
                if valeur < 0:
                    erreur("Impossible de calculer la racine carrée d'un nombre négatif.")
                import math
                return math.sqrt(valeur)
        
            noeud: Fonction = self.fonctions[un_cas.nom]
            arguments = []
            valeur_retour = ""
            for arg in un_cas.arguments:
                arguments.append(self.evaluer_expression(arg))
            ancien_env = self.env_courant
            env_fonction = Environnement(parent=None)
            self.env_courant = env_fonction

            for parametre, arg in zip(noeud.parametres, arguments):
                self.env_courant.definir(parametre.nom, arg)
            for decl in noeud.declarations:
                self.executer_instruction(decl)

            try:
                for inst in noeud.corps:
                    self.executer_instruction(inst)
            except SignalRetour as e:
                valeur_retour = e.valeur

            self.env_courant = ancien_env
            return valeur_retour

        if isinstance(un_cas, Indexation):
            tableau = self.env_courant.obtenir(un_cas.nom)
            indices = self.evaluer_expression(un_cas.indices[0])
            if not isinstance(indices, int):
                erreur(f"{un_cas.nom} : les indices d'un tableau doivent toujours être des entiers.")
            return tableau[indices]

    def operation_binaire(self, gauche, droite, operateur):
        def verifie_zero(droite) -> None:
            if droite == 0 or droite == 0.0:
                erreur("Division par zéro détectée à l'exécution")
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
        def aide_moi(type):
            match type:
                case "entier": valeur = 0
                case "reel": valeur = 0.0
                case "chaine": valeur = ""
                case "booleen": valeur = "vrai"
                case "caractere": valeur = ' '
            return valeur

        if isinstance(inst, DeclarationConstante):
            self.tout_type[inst.nom] = inst.type
            self.env_courant.definir(inst.nom, self.evaluer_expression(inst.valeur))

        elif isinstance(inst, DeclarationVariable):
            self.tout_type[inst.nom] = inst.type
            self.env_courant.definir(inst.nom, aide_moi(inst.type))

        elif isinstance(inst, DeclarationTableau):
            self.tout_type[inst.nom] = inst.type
            tableau: list = []
            if inst.type is None:
                for element in inst.valeurs_initiales:
                    tableau.append(element)
            else:
                valeur = aide_moi(inst.type)
                dimension = self.evaluer_expression(inst.dimensions)
                for i in range(dimension):
                    tableau.append(valeur)
            self.env_courant.definir(inst.nom, tableau)
                
        elif isinstance(inst, Affectation):
            valeur = self.evaluer_expression(inst.valeur)
            nom = inst.cible.nom
            if isinstance(inst.cible, Identifiant):
                self.env_courant.modifier(nom, valeur)
            else:
                tableau: list = self.env_courant.obtenir(nom)
                indice: int = self.evaluer_expression(inst.cible.indices[0])
                tableau[indice] = valeur
                self.env_courant.modifier(nom, tableau)

        elif isinstance(inst, Ecrire): 
            self.ecrire(inst)

        elif isinstance(inst, Lire):
            for cible in inst.cibles:
                nom = cible.nom
                saisie = input()
                
                match self.tout_type[nom]:

                    case "entier":
                        try:
                            saisie = int(saisie)
                        except ValueError:
                            erreur(f"{nom} est un entier et ne peut pas recevoir '{saisie}'")

                    case "reel":
                        try:
                            saisie = float(saisie)
                        except ValueError:
                            erreur(f"{nom} est un réel et ne peut pas recevoir '{saisie}'")

                    case "booleen":
                        erreur("On ne peut pas affecter un contenu à un booléen: non pris en charge dans le langage EVA")
                    case "caractere":
                        if len(saisie) != 1:
                            erreur(f"{nom} est un caractère et ne peut recevoir qu'un seul élément")
        
                if isinstance(cible, Identifiant):
                    self.env_courant.modifier(nom, saisie)
                else:
                    tableau = self.env_courant.obtenir(nom)
                    indice = self.evaluer_expression(cible.indices[0])
                    tableau[indice] = saisie
                    self.env_courant.modifier(nom, tableau)

        elif isinstance(inst, Si):
            condition = self.evaluer_expression(inst.condition)
            if condition:
                for sub_inst in inst.alors:
                    self.executer_instruction(sub_inst)
            elif inst.sinon:
                for sub_inst in inst.sinon:
                    self.executer_instruction(sub_inst)

        elif isinstance(inst, Cas):
            valeur_cible = self.evaluer_expression(inst.expression)
            
            # Récupération du type EVA de la cible (via tout_type ou le type du nœud)
            type_cible = None
            if isinstance(inst.expression, Identifiant):
                type_cible = self.tout_type.get(inst.expression.nom)
        
            trouve = False
            for branche in inst.branches:
                valeur_branche = self.evaluer_expression(branche.valeur)
                
                # Vérification optionnelle de sécurité à l'exécution
                if type_cible == "caractere" and not isinstance(branche.valeur, Caractere):
                    erreur("Incompatibilité de type à l'exécution : la branche doit être un caractère entre simples quotes ' '.")
        
                if valeur_cible == valeur_branche:
                    trouve = True
                    for sub_inst in branche.instructions:
                        self.executer_instruction(sub_inst)
                    break
        
            if not trouve and inst.sinon:
                for sub_inst in inst.sinon:
                    self.executer_instruction(sub_inst)

        elif isinstance(inst, Pour):
            nom_indice = inst.indice.nom
            val_debut = self.evaluer_expression(inst.debut)
            val_fin = self.evaluer_expression(inst.fin)
            val_pas = self.evaluer_expression(inst.pas)

            self.env_courant.definir(nom_indice, val_debut)

            if val_pas > 0:
                while self.env_courant.obtenir(nom_indice) <= val_fin:
                    for sub_inst in inst.corps:
                        self.executer_instruction(sub_inst)
                    courant = self.env_courant.obtenir(nom_indice)
                    self.env_courant.modifier(nom_indice, courant + val_pas)
            elif val_pas < 0:
                erreur("Dans la boucle pour, le pas doit être toujours positif")

        elif isinstance(inst, TantQue):
            while self.evaluer_expression(inst.condition):
                for sub_inst in inst.corps:
                    self.executer_instruction(sub_inst)

        elif isinstance(inst, Repeter):
            while True:
                for sub_inst in inst.corps:
                    self.executer_instruction(sub_inst)
                if self.evaluer_expression(inst.condition):
                    break

        elif isinstance(inst, Retourne):
            valeur = self.evaluer_expression(inst.valeur)
            raise SignalRetour(valeur)

        elif isinstance(inst, AppelInstruction):
            procedure: Procedure = self.procedures[inst.nom]
            arguments = [self.evaluer_expression(arg) for arg in inst.arguments]

            ancien_env = self.env_courant
            env_proc = Environnement(parent=None)
            self.env_courant = env_proc

            for parametre, arg in zip(procedure.parametres, arguments):
                self.env_courant.definir(parametre.nom, arg)

            for decl in procedure.declarations:
                self.executer_instruction(decl)

            for sub_inst in procedure.corps:
                self.executer_instruction(sub_inst)

            self.env_courant = ancien_env
                                

        
    
