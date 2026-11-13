# EVA - Langage Algorithmique Pédagogique
# Copyright (C) 2026 SASORI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass, field
from TYPES_CREER.__parseur import *
from SEMANTIQUE.tables import TableSymboles
from SEMANTIQUE.symbole import Symbole

@dataclass
class AnalyseurSemantique:
    ast: Algorithme
    tables: TableSymboles = field(default_factory=TableSymboles)
    fonction_courante: Fonction | None = None

    # ✅ Lance l'analyse dès l'instanciation
    def __post_init__(self):
        self.visiter_algorithme()

    def visiter_algorithme(self) -> None:
        self.tables.entrer_portee()
        self.tables.noms_globaux.add(self.ast.nom)
        self.tables.noms_globaux.add("racine")
        self.tables.noms_globaux.add("sqrt")
        self.visiter_declarations(self.ast.declarations)
        
        # Passe 1 : Enregistrer toutes les signatures de fonctions et procédures
        for fonction in self.ast.fonctions:
            types_params: list[str] = []
            for p in fonction.parametres:
                if p.est_tableau:
                    types_params.append(f"tableau {p.type}")
                else:
                    types_params.append(p.type)
            
            if fonction.retour_est_tableau:
                type_retour = f"tableau {fonction.type_retour}"
            else:
                type_retour = fonction.type_retour
            
            self.tables.declarer(
                fonction.nom,
                Symbole(fonction.nom, type_retour, False, types_params, nature="fonction", est_initialise=True, ligne=fonction.ligne)
            )
        
        for procedure in self.ast.procedures:
            types_params: list[str] = []
            for p in procedure.parametres:
                if p.est_tableau:
                    types_params.append(f"tableau {p.type}")
                else:
                    types_params.append(p.type)
            
            self.tables.declarer(
                procedure.nom,
                Symbole(procedure.nom, "procedure", False, types_params, nature="procedure", est_initialise=True, ligne=procedure.ligne)
            )

        # Passe 2 : Analyser les corps des fonctions et procédures
        self.visiter_fonctions()
        self.visiter_procedures()
        
        # Analyse du corps principal
        self.visiter_corps()
        self.tables.sortir_portee()

    def contient_identifiant(self, expr) -> bool:
        """Vérifie si une expression contient un identifiant (variable ou constante)."""
        if isinstance(expr, Identifiant):
            return True
        if isinstance(expr, OperationBinaire):
            return self.contient_identifiant(expr.gauche) or self.contient_identifiant(expr.droite)
        if isinstance(expr, OperationUnaire):
            return self.contient_identifiant(expr.operande)
        return False

    def visiter_fonctions(self):
        for fonction in self.ast.fonctions:
            self.tables.entrer_portee()
            self.fonction_courante = fonction

            for param in fonction.parametres:
                if param.est_tableau:
                    self.tables.declarer(
                        param.nom,
                        Symbole(param.nom, param.type, nature="tableau", nb_dimensions=1, est_initialise=True, ligne=param.ligne)
                    )
                else:
                    self.tables.declarer(param.nom, Symbole(param.nom, param.type, nature="parametre", est_initialise=True, ligne=param.ligne))

            self.visiter_declarations(fonction.declarations)

            self.appel_instruction(fonction.corps)

            if not self.verifier_chemins_retour(fonction.corps):
                self.tables.erreur(f"La fonction '{fonction.nom}' ne garantit pas de 'retourne' dans tous ses chemins d'exécution.", fonction.ligne)

            for param in fonction.parametres:
                symbole = self.tables.rechercher(param.nom)
                if not symbole.est_utilise:
                    self.tables.erreur(f"Le paramètre {param.nom} n'est jamais utiliser dans la fonction {fonction.nom}", param.ligne)

            self.fonction_courante = None

            self.tables.sortir_portee()

    def verifier_chemins_retour(self, instructions: list[Instruction]) -> bool:
        """Parcourt les instructions pour garantir qu'un retour est inévitable."""
        for inst in instructions:
            if isinstance(inst, Retourne):
                return True
            elif isinstance(inst, Si):
                if inst.sinon:
                    retour_alors: bool = self.verifier_chemins_retour(inst.alors)
                    retour_sinon: bool = self.verifier_chemins_retour(inst.sinon)
                    if retour_alors and retour_sinon:
                        return True

            elif isinstance(inst, Cas):
                tous_retournent: bool = True
                for branche in inst.branches:
                    if not self.verifier_chemins_retour(branche.instructions):
                        tous_retournent = False
                        break
                if tous_retournent and inst.sinon and self.verifier_chemins_retour(inst.sinon):
                    return True
        return False

    def visiter_procedures(self):
        for procedure in self.ast.procedures:

            self.tables.entrer_portee()
            self.fonction_courante = None

            for param in procedure.parametres:
                if param.est_tableau:
                    self.tables.declarer(
                        param.nom,
                        Symbole(param.nom, param.type, nature="tableau", nb_dimensions=1, est_initialise=True, ligne=param.ligne)
                    )
                else:
                    self.tables.declarer(param.nom, Symbole(param.nom, param.type, nature="parametre", est_initialise=True, ligne=param.ligne))
            self.visiter_declarations(procedure.declarations)

            self.appel_instruction(procedure.corps)
            for param in procedure.parametres:
                symbole = self.tables.rechercher(param.nom)
                if not symbole.est_utilise:
                    self.tables.erreur(f"Le paramètre {param.nom} n'est jamais utiliser dans la procedure {procedure.nom}", param.ligne)

            self.tables.sortir_portee()

    def visiter_declarations(self, declarations) -> None:
        for decl in declarations:
            if isinstance(decl, DeclarationVariable):
                self.tables.declarer(decl.nom, Symbole(decl.nom, decl.type, nature="variable", ligne=decl.ligne))

            elif isinstance(decl, DeclarationConstante):
                # ✅ Empêche l'initialisation d'une constante par un autre Identifiant
                if self.contient_identifiant(decl.valeur):
                    self.tables.erreur(f"La constante '{decl.nom}' doit être initialisée par une valeur littérale directe, pas par une autre constante ou variable.", decl.ligne)

                type_constante = self.obtenir_type_expression(decl.valeur)
                self.tables.declarer(
                    decl.nom,
                    Symbole(
                        nom=decl.nom,
                        type=type_constante,
                        est_constante=True,
                        nature="constante",
                        est_initialise=True,
                        ligne=decl.ligne,
                    )
                )

            else:
                # Gestion des tableaux (DeclarationTableau)
                dims_statiques: list[int] = []

                if decl.dimensions is None:
                    # Tableau constant initialisé par une liste d'éléments
                    nb_dim = 1
                    type_tableau = None
                    if decl.valeurs_initiales:
                        dims_statiques.append(len(decl.valeurs_initiales))
                        if dims_statiques[0] <= 1:
                            self.tables.erreur(
                                f"Un tableau de constantes doit contenir au minimum deux éléments : {decl.nom}",
                                decl.ligne,
                            )
                        # Déduction du type et validation des éléments par le sémantique
                        type_tableau = self.obtenir_type_expression(decl.valeurs_initiales[0])
                        for elem in decl.valeurs_initiales[1:]:
                            if self.obtenir_type_expression(elem) != type_tableau:
                                self.tables.erreur("Tous les éléments d'un tableau constant doivent être du même type.", elem.ligne)

                    self.tables.declarer(
                        decl.nom,
                        Symbole(
                            nom=decl.nom,
                            type=type_tableau,
                            est_constante=True,
                            nature="tableau",
                            nb_dimensions=nb_dim,
                            est_initialise=True,
                            dimensions_statiques=dims_statiques,
                            ligne=decl.ligne,
                        )
                    )
                else:
                    # Tableau standard déclaré avec des dimensions
                    nb_dim = len(decl.dimensions)
                    for dim in decl.dimensions:
                        if isinstance(dim, Nombre):
                            dims_statiques.append(int(dim.valeur))
                            if int(dim.valeur) <= 1:
                                self.tables.erreur(f"Les dimensions du tableau {decl.nom} doivent etre > 1", decl.ligne)

                    self.tables.declarer(
                        decl.nom,
                        Symbole(
                            nom=decl.nom,
                            type=decl.type,
                            nature="tableau",
                            nb_dimensions=nb_dim,
                            dimensions_statiques=dims_statiques,
                            ligne=decl.ligne,
                        )
                    )


    def visiter_corps(self) -> None:
        for instruction in self.ast.corps:
            self.visiter_instruction(instruction)

    def visiter_instruction(self, instruction: Instruction) -> None:
        if isinstance(instruction, Affectation):
            self.visiter_affectation(instruction)
        elif isinstance(instruction, Ecrire):
            self.visiter_ecrire(instruction)
        elif isinstance(instruction, Lire):
            self.visiter_lire(instruction)
        elif isinstance(instruction, Si):
            self.visiter_si(instruction)
        elif isinstance(instruction, TantQue):
            self.visiter_tant_que(instruction)
        elif isinstance(instruction, Pour):
            self.visiter_pour(instruction)
        elif isinstance(instruction, Cas): # ✅ Ajouté
            self.visiter_cas(instruction)
        elif isinstance(instruction, Retourne):
            self.visiter_retourne(instruction)
        elif isinstance(instruction, Repeter): # ✅ Ajouté
            self.visiter_repeter(instruction)
        elif isinstance(instruction, AppelInstruction):
            self.visiter_appel_instruction(instruction)

    def visiter_affectation(self, instruction: Affectation) -> None:
        symbole: Symbole = self.tables.rechercher(instruction.cible.nom, instruction.ligne)
        symbole.est_utilise = True   # ✅ la cible d'une affectation est "utilisée"

        if symbole.est_verrouille:
            self.tables.erreur(f"Impossible de modifier '{symbole.nom}' car c'est l'indice d'une boucle 'pour' en cours d'exécution.", instruction.ligne)

        if symbole.nature == "procedure":
            self.tables.erreur(f"On ne peut pas affecter une procédure vu qu'elle ne retourne rien : {symbole.nom}", instruction.ligne)

        if symbole.nature == "tableau" and not isinstance(instruction.cible, Indexation):
            # ✅ Exception : T ← f(...) où f retourne un tableau
            if not isinstance(instruction.valeur, AppelFonction):
                self.tables.erreur(f"L'affectation globale du tableau '{symbole.nom}' est interdite. Vous devez copier les éléments un par un.", instruction.ligne)

        if symbole.est_constante:
            self.tables.erreur("Une constante est immuable donc par conséquent affectation impossible.", instruction.ligne)

        # Interdiction de l'affectation d'une variable à elle-même (ex: x <- x)
        if isinstance(instruction.cible, Identifiant) and isinstance(instruction.valeur, Identifiant):
            if instruction.cible.nom == instruction.valeur.nom:
                self.tables.erreur(f"Réaffectation d'une variable à elle-même interdite : '{instruction.cible.nom} <- {instruction.valeur.nom}' n'a pas de sens 🚫", instruction.ligne)

        # Interdiction de la réaffectation d'un élément de tableau à lui-même (ex: T(i) <- T(i))
        if isinstance(instruction.cible, Indexation) and isinstance(instruction.valeur, Indexation):
            if instruction.cible.nom == instruction.valeur.nom and instruction.cible.indices == instruction.valeur.indices:
                self.tables.erreur(f"Réaffectation de l'élément de tableau à lui-même interdite : '{instruction.cible.nom}' 🚫", instruction.ligne)

        if isinstance(instruction.cible, Indexation):

            if symbole.nature != "tableau":
                self.tables.erreur(f"La variable '{instruction.cible.nom}' est de type '{symbole.type}', ce n'est pas un tableau. Impossible d'utiliser des parenthèses. 🚫", instruction.ligne)

            
            self.visiter_indexation_statique(symbole, instruction.cible)
            if len(instruction.cible.indices) != symbole.nb_dimensions:
                self.tables.erreur(f"Le tableau '{symbole.nom}' attend {symbole.nb_dimensions} dimension(s), mais {len(instruction.cible.indices)} ont été fournies.", instruction.ligne)
            for indice in instruction.cible.indices:
                if self.obtenir_type_expression(indice) != "entier":
                    self.tables.erreur("L'indice d'un tableau doit être de type entier.", instruction.ligne)

        type_affecte = self.obtenir_type_expression(instruction.valeur)
        
        # Le type "cible" dépend de ce qu'on affecte
        if isinstance(instruction.cible, Indexation):
            # ✅ Une case de tableau a le type scalaire (reel, entier, ...)
            type_cible = symbole.type
        else:
            # ✅ Le tableau entier (via AppelFonction) a le type "tableau X"
            type_cible = f"tableau {symbole.type}" if symbole.nature == "tableau" else symbole.type
        
        if type_cible != type_affecte:
            if not (type_cible == "reel" and type_affecte == "entier"):
                self.tables.erreur(f"Type incompatible : impossible d'affecter un '{type_affecte}' à une variable de type '{type_cible}'.", instruction.ligne)

        symbole.est_initialise = True

    def visiter_ecrire(self, instruction: Ecrire) -> None:
        for element in instruction.arguments :
            self.obtenir_type_expression(element)

    def visiter_lire(self, instruction: Lire) -> None:
        for element in instruction.cibles :
            symbole: Symbole = self.tables.rechercher(element.nom, instruction.ligne)
            if symbole.est_constante:
                self.tables.erreur("Impossible de lire dans une constante.", instruction.ligne)
            if symbole.type == "booleen":
                self.tables.erreur("On ne peut pas lire un booléen. Veuillez faire une affectation directe.", instruction.ligne)
            if symbole.est_verrouille:
                self.tables.erreur(f"Impossible de modifier '{symbole.nom}' via 'lire' car c'est l'indice d'une boucle 'pour' en cours d'exécution. 🚫", instruction.ligne)
            if isinstance(element, Indexation):
                for args in element.indices:
                    self.obtenir_type_expression(args)

            symbole.est_initialise = True
            symbole.est_lu = True

    def simplifier(self, expr: Expression) -> Expression:
        if isinstance(expr, OperationUnaire):
            if expr.operateur == "+":
                return self.simplifier(expr.operande)

            if expr.operateur == "-" and isinstance(expr.operande, OperationUnaire) and expr.operande.operateur == "-":
                return self.simplifier(expr.operande.operande)

            if expr.operateur == "-" and isinstance(expr.operande, OperationUnaire):
                return self.simplifier(expr.operande)

            return OperationUnaire(expr.operateur, self.simplifier(expr.operande))

        if isinstance(expr, OperationBinaire):
            return OperationBinaire(expr.operateur, self.simplifier(expr.gauche), self.simplifier(expr.droite))

        return expr

    def est_tautologie(self, condition) -> bool:
        if not isinstance(condition, OperationBinaire):
            return False
        if condition.operateur not in ("=", "<=", ">=", "<", ">", "<>"):
            return False

        if condition.operateur in ("=", "<=", ">=", "<", ">", "<>"):
            gauche_simplifier = self.simplifier(condition.gauche)
            droite_simplifier = self.simplifier(condition.droite)

            if droite_simplifier == gauche_simplifier:
                return True

        return False

    def verifier_pas_tautologie(self, condition):
        if self.est_tautologie(condition) :
            self.tables.erreur("Comparaison tautologique détectée : les deux côtés sont identiques 🚫", condition.ligne)
            

    def visiter_si(self, instruction: Si) -> None:
        if self.obtenir_type_expression(instruction.condition, est_condition=False) != "booleen":
            self.tables.erreur("Une condition doit toujours produire un booleen", instruction.ligne)

        self.verifier_pas_tautologie(instruction.condition)
        # Sauvegarde des états d'initialisation avant le bloc Si
        etat_initial = {nom: sym.est_initialise for nom, sym in self.tables.pile[-1].items()}

        # Visite du bloc 'alors'
        self.appel_instruction(instruction.alors)
        etat_apres_alors = {nom: sym.est_initialise for nom, sym in self.tables.pile[-1].items()}

        # Restauration pour le bloc 'sinon'
        for nom, est_init in etat_initial.items():
            self.tables.pile[-1][nom].est_initialise = est_init

        # Visite du bloc 'sinon'
        if instruction.sinon:
            self.appel_instruction(instruction.sinon)
            etat_apres_sinon = {nom: sym.est_initialise for nom, sym in self.tables.pile[-1].items()}
            
            # Intersection : Initialisé après le Si SEULEMENT si initialisé dans Alors ET Sinon
            for nom in etat_initial:
                self.tables.pile[-1][nom].est_initialise = etat_apres_alors[nom] and etat_apres_sinon[nom]
        else:
            # Sans sinon, l'initialisation dans 'alors' ne garantit rien pour la suite
            for nom, est_init in etat_initial.items():
                self.tables.pile[-1][nom].est_initialise = est_init


    def visiter_tant_que(self, instruction: TantQue) -> None:
        if self.obtenir_type_expression(instruction.condition) != "booleen":
            self.tables.erreur("La condition de la boucle 'tant que' doit toujours produire un booleen", instruction.ligne)

        self.verifier_pas_tautologie(instruction.condition)
        # Sauvegarde de l'état (la boucle pouvant s'exécuter 0 fois)
        etat_initial = {nom: sym.est_initialise for nom, sym in self.tables.pile[-1].items()}

        self.appel_instruction(instruction.corps)

        # Restauration pour la suite du programme
        for nom, est_init in etat_initial.items():
            self.tables.pile[-1][nom].est_initialise = est_init

    def visiter_pour(self, instruction: Pour) -> None:
        symbole: Symbole = self.tables.rechercher(instruction.indice.nom, instruction.ligne)
        
        if symbole.type != "entier":
            self.tables.erreur(f"L'indice de la boucle 'pour' ('{symbole.nom}') doit être de type entier, pas '{symbole.type}'. 🚫", instruction.ligne)

        if symbole.est_verrouille:
            self.tables.erreur(
                f"L'indice '{symbole.nom}' est déjà utilisé par une boucle englobante. "
                f"Utilisez un nom différent pour la boucle imbriquée // Index '{symbole.nom}' already used by an enclosing loop 🚫",
                instruction.ligne
            )

        symbole.est_initialise = True
        symbole.est_utilise = True
        symbole.est_verrouille = True
        
        type_debut = self.obtenir_type_expression(instruction.debut)
        type_fin = self.obtenir_type_expression(instruction.fin)
        type_pas = self.obtenir_type_expression(instruction.pas)

        if isinstance(instruction.pas, Nombre) and instruction.pas.valeur <= 0:
            self.tables.erreur("Le pas d'une boucle 'pour' doit être strictement positif // The 'pour' loop step must be strictly positive 🚫", instruction.ligne) 

        if isinstance(instruction.debut, Nombre) and isinstance(instruction.fin, Nombre):
            if not (instruction.debut.valeur <= instruction.fin.valeur):
                self.tables.erreur("Boucle 'pour' impossible : début > fin, la boucle ne s'exécutera jamais // Impossible 'pour' loop: start > end, loop will never run 🚫", instruction.ligne)

        if type_debut != "entier" or type_fin != "entier" or type_pas != "entier":
            self.tables.erreur("Les bornes (début, fin) et le pas d'une boucle 'pour' doivent tous être de type entier. 🚫", instruction.ligne)

        self.appel_instruction(instruction.corps)
        symbole.est_verrouille = False

    def visiter_retourne(self, instruction: Retourne) -> None:
        if self.fonction_courante is None:
            self.tables.erreur("L'instruction 'retourne' est interdite dans une procédure.", instruction.ligne)

        type_retour_attendu: str = f"tableau {self.fonction_courante.type_retour}" if self.fonction_courante.retour_est_tableau else self.fonction_courante.type_retour
        type_retour_reel: str = self.obtenir_type_expression(instruction.valeur)

        if type_retour_attendu != type_retour_reel:
            self.tables.erreur(f"Type de retour invalide : la fonction attend '{type_retour_attendu}', mais l'expression est de type '{type_retour_reel}'.", instruction.ligne)

    def visiter_branche_cas(self, type_: str, une_branche: BrancheCas) -> None:
        type_branche = self.obtenir_type_expression(une_branche.valeur)
        
        # Interdiction stricte : un 'caractere' ne peut pas être comparé à une 'chaine' "A"
        if type_ != type_branche:
            self.tables.erreur(
                f"Incompatibilité de type dans la structure 'cas' : "
                f"l'expression cible est de type '{type_}', mais la branche propose une valeur de type '{type_branche}' 🚫",
                une_branche.ligne,
            )
    
        self.appel_instruction(une_branche.instructions)

    def appel_instruction(self, grande_instruction: list[Instruction]) -> None:
        if grande_instruction:
            retour_rencontrer: bool = False
            for instruction in grande_instruction:
                if retour_rencontrer:
                    self.tables.erreur("Code inaccessible détecté après une instruction 'retourne' 🚫", instruction.ligne)
                    
                self.visiter_instruction(instruction)
                if isinstance(instruction, Retourne):
                    retour_rencontrer = True

    def visiter_indexation_statique(self, symbole: Symbole, indexation: Indexation):
        # Si les indices sont des nombres littéraux et que les dimensions sont connues
        for i, indice_expr in enumerate(indexation.indices):
            if isinstance(indice_expr, Nombre) and i < len(symbole.dimensions_statiques):
                taille_max = symbole.dimensions_statiques[i]
                if indice_expr.valeur < 0 or indice_expr.valeur > taille_max:
                    self.tables.erreur(
                        f"Débordement de tableau détecté à la compilation : "
                        f"indice {indice_expr.valeur} hors des bornes [1..{taille_max - 1}] pour '{symbole.nom}' 🚫",
                        symbole.ligne
                    )

    def visiter_cas(self, instruction: Cas) -> None:
        type_expression = self.obtenir_type_expression(instruction.expression)
        
        etat_initial = {nom: sym.est_initialise for nom, sym in self.tables.pile[-1].items()}
        etats_branches = []

        for element in instruction.branches:
            # Restauration de l'état initial avant chaque branche
            for nom, est_init in etat_initial.items():
                self.tables.pile[-1][nom].est_initialise = est_init
                
            self.visiter_branche_cas(type_expression, element)
            etats_branches.append({nom: sym.est_initialise for nom, sym in self.tables.pile[-1].items()})

        if instruction.sinon:
            for nom, est_init in etat_initial.items():
                self.tables.pile[-1][nom].est_initialise = est_init
            self.appel_instruction(instruction.sinon)
            etats_branches.append({nom: sym.est_initialise for nom, sym in self.tables.pile[-1].items()})

        # Une variable n'est initialisée que si elle l'est dans TOUTES les branches et le sinon
        for nom in etat_initial:
            self.tables.pile[-1][nom].est_initialise = all(branche[nom] for branche in etats_branches)

    def visiter_repeter(self, instruction) -> None:
        self.appel_instruction(instruction.corps)
        if self.obtenir_type_expression(instruction.condition) != "booleen" :
            self.tables.erreur("Une condition doit toujours donner un booléen.", instruction.ligne)

        self.verifier_pas_tautologie(instruction.condition)

    def visiter_appel_instruction(self, instruction: AppelInstruction) -> None:
        symbole: Symbole = self.tables.rechercher(instruction.nom, instruction.ligne)
        if symbole.nature != "procedure":
            self.tables.erreur(f"L'identifiant '{instruction.nom}' n'est pas une procédure appelable.", instruction.ligne)
            
        arguments: list = []
        for element in instruction.arguments:
            arguments.append(self.obtenir_type_expression(element))
        if len(arguments) == len(symbole.parametres):
            for i, j in zip(arguments, symbole.parametres):
                if i != j:
                    self.tables.erreur("Les types declarer au niveaux des arguments d'une procédure doivent être respecter à l'appel", instruction.ligne)
        else:
            self.tables.erreur("Le nombre de paramètre des procedures doivent être egale au nombre passer en paramètre", instruction.ligne)
        symbole.est_utilise = True

    def obtenir_type_expression(self, expr: Expression, est_condition: bool = False) -> str:
        if isinstance(expr, Nombre):
            return "entier" if isinstance(expr.valeur, int) else "reel"
        elif isinstance(expr, Caractere):
            return "caractere"
        elif isinstance(expr, ChaineCaractere):
            return "chaine"
        elif isinstance(expr, Booleen):
            return "booleen"
        elif isinstance(expr, Identifiant):
            symbole = self.tables.rechercher(expr.nom, expr.ligne)
            if not symbole.est_initialise:
                self.tables.erreur(f"La variable '{expr.nom}' est utilisée avant d'être initialisée 🚫", expr.ligne)
            symbole.est_utilise = True
            if not est_condition:
                symbole.est_consomme = True
            if symbole.nature == "tableau":
                return f"tableau {symbole.type}"
            return symbole.type

        elif isinstance(expr, Indexation):
            symbole = self.tables.rechercher(expr.nom, expr.ligne)

            if symbole.nature != "tableau":
                self.tables.erreur(f"La variable '{expr.nom}' est de type '{symbole.type}', ce n'est pas un tableau. Impossible d'utiliser des parenthèses. 🚫", expr.ligne)

            
            if not symbole.est_initialise:
                self.tables.erreur(f"Le tableau '{expr.nom}' est utilisé avant d'être initialisé 🚫", expr.ligne)

            symbole.est_utilise = True

            if not est_condition:
                symbole.est_consomme = True

            for indice in expr.indices:
                if self.obtenir_type_expression(indice, est_condition) != "entier":
                    self.tables.erreur("L'indice d'un tableau doit être un entier.", expr.ligne)
            return symbole.type
        elif isinstance(expr, AppelFonction):
            if expr.nom in ("racine", "sqrt"):
                if len(expr.arguments) != 1:
                    self.tables.erreur("La fonction 'racine/sqrt' prend exactement un argument.", expr.ligne)
                type_arg = self.obtenir_type_expression(expr.arguments[0])

                if type_arg not in ("entier", "reel"):
                    self.tables.erreur(f"L'argument de 'racine' doit être numérique, pas '{type_arg}'.", expr.ligne)

                return "reel"

            symbole = self.tables.rechercher(expr.nom, expr.ligne)
            symbole.est_utilise = True

            # ✅ CAS 1 : C'est un tableau → c'est une indexation
            if symbole.nature == "tableau":
                for arg in expr.arguments:
                    if self.obtenir_type_expression(arg, est_condition=False) != "entier":
                        self.tables.erreur(f"L'indice du tableau '{expr.nom}' doit être un entier.", expr.ligne)
                return symbole.type

            # ✅ CAS 2 : C'est une fonction → c'est un appel
            if symbole.nature == "fonction":
                for arg in expr.arguments:
                    self.obtenir_type_expression(arg, est_condition=False)
                return symbole.type

            self.tables.erreur(f"'{expr.nom}' n'est ni une fonction ni un tableau. Impossible d'utiliser des parenthèses. 🚫", expr.ligne)

        elif isinstance(expr, OperationBinaire):
            type_g = self.obtenir_type_expression(expr.gauche, est_condition)
            if expr.operateur in ("/", "div", "mod"):
                if isinstance(expr.droite, Nombre) and expr.droite.valeur == 0:
                    self.tables.erreur("Division par zéro détectée à la compilation // Division by zero at compile time 🚫", expr.ligne)
            type_d = self.obtenir_type_expression(expr.droite, est_condition)
            
            if expr.operateur in ("=", "<>", "<", ">", "<=", ">="):
                return "booleen"
            elif expr.operateur in ("et", "ou"):
                if type_g != "booleen" or type_d != "booleen":
                    self.tables.erreur(f"Les opérateurs 'et'/'ou' exigent des booléens, pas '{type_g}' et '{type_d}'.", expr.ligne)
                return "booleen"
            elif expr.operateur in ("+", "-", "*", "/", "div", "mod", "^"):
                if expr.operateur == "/":
                    return "reel"
                if expr.operateur in ("div", "mod"): # return toujours des entiers même si des réels les appels.
                    if not (type_g in ("entier", "reel")) or not (type_d in ("entier", "reel")):
                        self.tables.erreur(f"L'opérateur '{expr.operateur}' exige deux nombres.", expr.ligne)
                    return "entier"
                return "entier" if type_g != "reel" and type_d != "reel" else "reel"
        elif isinstance(expr, OperationUnaire):
            type_op = self.obtenir_type_expression(expr.operande, est_condition)
            if expr.operateur == "non":
                if type_op != "booleen":
                    self.tables.erreur("L'opérateur 'non' s'applique uniquement à un booléen.", expr.ligne)
                return "booleen"
            return type_op
        
        self.tables.erreur("Inconnu", expr.ligne)
