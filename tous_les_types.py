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
    parametres: list[str] = field(default_factory=list)
    nature: str = "variable"
    nb_dimensions: int = 0
    # --- NOUVEAUTÉS ---
    est_initialise: bool = False
    est_utilise: bool = False
    est_verrouille: bool = False
    dimensions_statiques: list[int] = field(default_factory=list)

@dataclass
class TableSymboles:
    pile: list[dict[str, Symbole]] = field(default_factory=list)
    symboles_globaux: set[str] = field(default_factory=set)

    def entrer_portee(self) -> None:
        self.pile.append({})

    def sortir_portee(self) -> None:
        portee_actuelle: dict = self.pile[-1]

        for nom, symbole in portee_actuelle.items():
            if not symbole.est_utilise and symbole.nature in ("variable", "constante", "tableau", "fonction", "procedure"):

                match symbole.nature:
                    case "variable": vrai_nom = "La variable"
                    case "constante": vrai_nom = "La constante"
                    case "tableau": vrai_nom = "Le tableau"
                    case "fonction": vrai_nom = "La fonction"
                    case "procedure": vrai_nom = "La procedure"
                    case _ : vrai_nom = symbole
                self.erreur(f"{vrai_nom}  '{nom}' est déclaré mais jamais utilisé 🚫")
        self.pile.pop()

    def declarer(self, nom: str, symbole: Symbole) -> None:
        if nom in self.symboles_globaux:
            self.erreur(f"Le symbole '{nom}' est déjà déclaré dans le programme (Nom unique obligatoire dans EVA) 🚫 : NB: aucune donnée ne doit avoir le nom de votre algortihme.")
        self.symboles_globaux.add(nom)
        self.pile[-1][nom] = symbole

    def rechercher(self, nom: str) -> Symbole:
        for portee in reversed(self.pile):
            if nom in portee:
                return portee[nom]
        self.erreur(f"Le symbole '{nom}' n'est pas déclaré 🚫")

    def erreur(self, message: str ="") -> None:
        message = f"Analyseur_semantique → {message}"
        erreur(message)

@dataclass
class AnalyseurSemantique:
    ast: Algorithme
    tables: TableSymboles = field(default_factory=TableSymboles)
    fonction_courante: Fonction | None = None

    def visiter_algorithme(self) -> None:
        self.tables.entrer_portee()
        self.tables.symboles_globaux.add(self.ast.nom)
        self.visiter_declarations(self.ast.declarations)
        
        # Passe 1 : Enregistrer toutes les signatures de fonctions et procédures
        for fonction in self.ast.fonctions:
            self.tables.declarer(
                fonction.nom, 
                Symbole(fonction.nom, fonction.type_retour, False, [p.type for p in fonction.parametres], nature="fonction", est_initialise=True)
            )
        for procedure in self.ast.procedures:
            self.tables.declarer(
                procedure.nom, 
                Symbole(procedure.nom, "procedure", False, [p.type for p in procedure.parametres], nature="procedure", est_initialise=True)
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
                self.tables.declarer(param.nom, Symbole(param.nom, param.type, nature="parametre", est_initialise=True))

            self.visiter_declarations(fonction.declarations)

            self.appel_instruction(fonction.corps)

            if not self.verifier_chemins_retour(fonction.corps):
                self.tables.erreur(f"La fonction '{fonction.nom}' ne garantit pas de 'retourne' dans tous ses chemins d'exécution.")
            
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
                self.tables.declarer(param.nom, Symbole(param.nom, param.type, nature="parametre", est_initialise=True))

            self.visiter_declarations(procedure.declarations)

            self.appel_instruction(procedure.corps)

            self.tables.sortir_portee()

    def visiter_declarations(self, declarations) -> None:
        for decl in declarations:
            if isinstance(decl, DeclarationVariable):
                self.tables.declarer(decl.nom, Symbole(decl.nom, decl.type, nature="variable"))

            elif isinstance(decl, DeclarationConstante):
                # ✅ Empêche l'initialisation d'une constante par un autre Identifiant
                if self.contient_identifiant(decl.valeur):
                    self.tables.erreur(f"La constante '{decl.nom}' doit être initialisée par une valeur littérale directe, pas par une autre constante ou variable.")

                type_constante = self.obtenir_type_expression(decl.valeur)
                self.tables.declarer(
                    decl.nom,
                    Symbole(
                        nom=decl.nom,
                        type=type_constante,
                        est_constante=True,
                        nature="constante",
                        est_initialise=True
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
                        # Déduction du type et validation des éléments par le sémantique
                        type_tableau = self.obtenir_type_expression(decl.valeurs_initiales[0])
                        for elem in decl.valeurs_initiales[1:]:
                            if self.obtenir_type_expression(elem) != type_tableau:
                                self.tables.erreur("Tous les éléments d'un tableau constant doivent être du même type.")

                    self.tables.declarer(
                        decl.nom,
                        Symbole(
                            nom=decl.nom,
                            type=type_tableau,
                            est_constante=True,
                            nature="tableau",
                            nb_dimensions=nb_dim,
                            est_initialise=True,
                            dimensions_statiques=dims_statiques
                        )
                    )
                else:
                    # Tableau standard déclaré avec des dimensions
                    nb_dim = len(decl.dimensions)
                    for dim in decl.dimensions:
                        if isinstance(dim, Nombre):
                            dims_statiques.append(int(dim.valeur))

                    self.tables.declarer(
                        decl.nom,
                        Symbole(
                            nom=decl.nom,
                            type=decl.type,
                            nature="tableau",
                            nb_dimensions=nb_dim,
                            dimensions_statiques=dims_statiques
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
        symbole: Symbole = self.tables.rechercher(instruction.cible.nom)

        if symbole.est_verrouille:
            self.tables.erreur(f"Impossible de modifier '{symbole.nom}' car c'est l'indice d'une boucle 'pour' en cours d'exécution.")

        if symbole.nature == "procedure":
            self.tables.erreur(f"On ne peut pas affecter une procedure vu qu'elle ne retourne rien. {symbole.nom} ")

        if symbole.nature == "tableau" and not isinstance(instruction.cible, Indexation):
            self.tables.erreur(f"L'affectation globale du tableau '{symbole.nom}' est interdite. Vous devez copier les éléments un par un un conseil utiliser une boucle.")

        if symbole.est_constante :
            self.tables.erreur("Une constante est immuable donc par consequent affectation impossible.")

        type_affecte = self.obtenir_type_expression(instruction.valeur)
        if symbole.type != type_affecte:
            # ✅ Règle : Un Entier peut être affecté dans un Réel, mais pas l'inverse.
            if not (symbole.type == "reel" and type_affecte == "entier"):
                self.tables.erreur(f"Type incompatible : impossible d'affecter un '{type_affecte}' à une variable de type '{symbole.type}'.")

        if isinstance(instruction.cible, Indexation):
            if symbole.nature != "tableau":
                self.tables.erreur(f"'{instruction.cible.nom}' n'est pas un tableau, indexation impossible.")

            self.visiter_indexation_statique(symbole, instruction.cible)

            if len(instruction.cible.indices) != symbole.nb_dimensions:
                self.tables.erreur(f"Le tableau '{symbole.nom}' attend {symbole.nb_dimensions} dimension(s), mais {len(instruction.cible.indices)} ont été fournies.")

            for indice in instruction.cible.indices :
                if self.obtenir_type_expression(indice) != "entier":
                    self.tables.erreur("L'indice d'un tableau doit être de type entier.")

        symbole.est_initialise = True

    def visiter_ecrire(self, instruction: Ecrire) -> None:
        for element in instruction.arguments :
            self.obtenir_type_expression(element)

    def visiter_lire(self, instruction: Lire) -> None:
        for element in instruction.cibles :
            symbole: Symbole = self.tables.rechercher(element.nom)
            if symbole.est_constante:
                self.tables.erreur("Impossible de lire dans une constante.")
            if symbole.est_verrouille:
                self.tables.erreur(f"Impossible de modifier '{symbole.nom}' via 'lire' car c'est l'indice d'une boucle 'pour' en cours d'exécution. 🚫")
            if isinstance(element, Indexation):
                for args in element.indices:
                    self.obtenir_type_expression(args)

            symbole.est_initialise = True


    def visiter_si(self, instruction: Si) -> None:
        if self.obtenir_type_expression(instruction.condition) != "booleen":
            self.tables.erreur("Une condition doit toujours produire un booleen")

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
            self.tables.erreur("La condition de la boucle 'tant que' doit toujours produire un booleen")

        # Sauvegarde de l'état (la boucle pouvant s'exécuter 0 fois)
        etat_initial = {nom: sym.est_initialise for nom, sym in self.tables.pile[-1].items()}

        self.appel_instruction(instruction.corps)

        # Restauration pour la suite du programme
        for nom, est_init in etat_initial.items():
            self.tables.pile[-1][nom].est_initialise = est_init

    def visiter_pour(self, instruction: Pour) -> None:
        symbole: Symbole = self.tables.rechercher(instruction.indice.nom)
        
        if symbole.type != "entier":
            self.tables.erreur(f"L'indice de la boucle 'pour' ('{symbole.nom}') doit être de type entier, pas '{symbole.type}'. 🚫")

        symbole.est_initialise = True
        symbole.est_utilise = True
        symbole.est_verrouille = True
        
        type_debut = self.obtenir_type_expression(instruction.debut)
        type_fin = self.obtenir_type_expression(instruction.fin)
        type_pas = self.obtenir_type_expression(instruction.pas)

        if type_debut != "entier" or type_fin != "entier" or type_pas != "entier":
            self.tables.erreur("Les bornes (début, fin) et le pas d'une boucle 'pour' doivent tous être de type entier. 🚫")

        self.appel_instruction(instruction.corps)
        symbole.est_verrouille = False

    def visiter_retourne(self, instruction: Retourne) -> None:
        if self.fonction_courante is None:
            self.tables.erreur("L'instruction 'retourne' est interdite dans une procédure.")

        type_retour_attendu: str = self.fonction_courante.type_retour
        type_retour_reel: str = self.obtenir_type_expression(instruction.valeur)

        if type_retour_attendu != type_retour_reel:
            self.tables.erreur(f"Type de retour invalide : la fonction attend '{type_retour_attendu}', mais l'expression est de type '{type_retour_reel}'.")

    def visiter_branche_cas(self, type_: str, une_branche: BrancheCas) -> None:
        if type_ != self.obtenir_type_expression(une_branche.valeur):
            self.tables.erreur("la comparaison à l'aide du cas se fait entre élément de même type.")

        self.appel_instruction(une_branche.instructions)

    def appel_instruction(self, grande_instruction: list[Instruction]) -> None:
        if grande_instruction:
            retour_rencontrer: bool = False
            for instruction in grande_instruction:
                if retour_rencontrer:
                    self.tables.erreur("Code inaccessible détecté après une instruction 'retourne' 🚫")
                    
                self.visiter_instruction(instruction)
                if isinstance(instruction, Retourne):
                    retour_rencontrer = True

    def visiter_indexation_statique(self, symbole: Symbole, indexation: Indexation):
        # Si les indices sont des nombres littéraux et que les dimensions sont connues
        for i, indice_expr in enumerate(indexation.indices):
            if isinstance(indice_expr, Nombre) and i < len(symbole.dimensions_statiques):
                taille_max = symbole.dimensions_statiques[i]
                if indice_expr.valeur < 1 or indice_expr.valeur > taille_max:
                    self.tables.erreur(
                        f"Débordement de tableau détecté à la compilation : "
                        f"indice {indice_expr.valeur} hors des bornes [1..{taille_max}] pour '{symbole.nom}' 🚫"
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
            self.tables.erreur("Une condition doit toujours donner un booléen.")

    def visiter_appel_instruction(self, instruction: AppelInstruction) -> None:
        symbole: Symbole = self.tables.rechercher(instruction.nom)
        if symbole.nature != "procedure":
            self.tables.erreur(f"L'identifiant '{instruction.nom}' n'est pas une procédure appelable.")
            
        arguments: list = []
        for element in instruction.arguments:
            arguments.append(self.obtenir_type_expression(element))
        if len(arguments) == len(symbole.parametres):
            for i, j in zip(arguments, symbole.parametres):
                if i != j:
                    self.tables.erreur("Les types declarer au niveaux des arguments d'une procédure doivent être respecter à l'appel")
        else:
            self.tables.erreur("Le nombre de paramètre des procedures doivent être egale au nombre passer en paramètre")
        symbole.est_utilise = True

    def obtenir_type_expression(self, expr: Expression) -> str:
        if isinstance(expr, Nombre):
            return "entier" if isinstance(expr.valeur, int) else "reel"

        if isinstance(expr, Caractere):
            return "caractere"

        if isinstance(expr, ChaineCaractere):
            return "chaine"

        if isinstance(expr, Booleen):
            return "booleen"

        if isinstance(expr, Identifiant):
            # C'est ici qu'on s'assure que la variable existe !
            symbole = self.tables.rechercher(expr.nom)
            if not symbole.est_initialise:
                self.tables.erreur(f"La variable '{expr.nom}' est lue avant d'avoir été initialisée ! 🚫")

            symbole.est_utilise = True
            return symbole.type

        if isinstance(expr, Indexation):
            symbole = self.tables.rechercher(expr.nom)
            if not symbole.est_initialise:
                self.tables.erreur(f"La variable '{expr.nom}' est lue avant d'avoir été initialisée ! 🚫")

            if len(expr.indices) != symbole.nb_dimensions:
                self.tables.erreur(f"Le tableau '{symbole.nom}' attend {symbole.nb_dimensions} dimension(s).")

            for indice in expr.indices:
                if self.obtenir_type_expression(indice) != "entier":
                    self.tables.erreur(f"L'indice du tableau '{expr.nom}' doit être de type entier.")
                
            self.visiter_indexation_statique(symbole, expr)
            symbole.est_utilise = True
            return symbole.type

        if isinstance(expr, OperationBinaire):
            type_gauche: str = self.obtenir_type_expression(expr.gauche)
            type_droite: str = self.obtenir_type_expression(expr.droite)

            if expr.operateur in ("+", "-", "*", "/", "div", "mod", "^"):
                if expr.operateur in ("/", "div", "mod") and isinstance(expr.droite, Nombre) and (expr.droite.valeur == 0 or expr.droite.valeur == 0.0):
                    self.tables.erreur("Division par zéro détectée avant compilation")

                if expr.operateur in ("div", "mod"):
                    if type_gauche not in ("entier", "reel") or type_droite not in ("entier", "reel"):
                        self.tables.erreur(f"L'opérateur '{expr.operateur}' exige des entiers, pas '{type_gauche}' et '{type_droite}'.")
                    return "entier"

                if expr.operateur == "/":
                    if type_gauche not in ("entier", "reel") or type_droite not in ("entier", "reel"):
                        self.tables.erreur(f"L'opérateur '/' exige des types numériques, pas '{type_gauche}' et '{type_droite}'.")
                    return "reel"

                if type_gauche == "reel" or type_droite == "reel":
                    if type_gauche not in ("entier", "reel") or type_droite not in ("entier", "reel"):
                        self.tables.erreur("Opération arithmétique impossible sur des types non numériques.")
                    return "reel"
                elif type_gauche == "entier" and type_droite == "entier":
                    return "entier"
                else:
                    self.tables.erreur("Opération incohérente et non supportée par le langage.")
        
        if isinstance(expr, OperationUnaire):
            type_operande: str = self.obtenir_type_expression(expr.operande)
            operateur: str = expr.operateur

            if operateur == "non":
                if type_operande != "booleen":
                    self.tables.erreur(f"L'opérateur 'non' requiert un booleen, pas un '{type_operande}' 🚫")
                return "booleen"
            elif type_operande in ("entier", "reel"):
                return "entier" if type_operande == "entier" else "reel"
            self.tables.erreur(f"Type d'expression non pris en charge ou invalide : {type(expr).__name__}")

        if isinstance(expr, AppelFonction):
            symbole: Symbole = self.tables.rechercher(expr.nom)
            symbole.est_utilise = True
            
            # Cas 1 : C'est en fait un tableau
            if symbole.nature == "tableau":
                if len(expr.arguments) != symbole.nb_dimensions:
                    self.tables.erreur(f"Le tableau '{expr.nom}' attend {symbole.nb_dimensions} dimension(s).")
                if not symbole.est_initialise:
                    self.tables.erreur(f"Le tableau '{expr.nom}' est lu avant d'avoir été initialisé ! 🚫")
                for element in expr.arguments:
                    if self.obtenir_type_expression(element) != "entier":
                        self.tables.erreur(f"L'indice du tableau '{expr.nom}' doit être de type entier.")
                        
                self.visiter_indexation_statique(symbole, Indexation(expr.nom, expr.arguments))
                return symbole.type

            elif symbole.nature == "procedure":
                self.tables.erreur(f"Impossible d'utiliser la procédure '{expr.nom}' dans une expression car elle ne retourne aucune valeur.")

            # Cas 2 : C'est bien une fonction
            elif symbole.nature == "fonction":
                arguments: list = []
                for element in expr.arguments:
                    arguments.append(self.obtenir_type_expression(element))
                if len(arguments) == len(symbole.parametres):
                    for i, j in zip(arguments, symbole.parametres):
                        if i != j:
                            self.tables.erreur(f"Erreur de type dans l'appel de '{expr.nom}' : attendu {j}, reçu {i}.")
                    return symbole.type
                else:
                    self.tables.erreur(f"La fonction '{expr.nom}' attend {len(symbole.parametres)} argument(s), mais {len(arguments)} ont été fournis.")
            else:
                self.tables.erreur(f"'{expr.nom}' n'est ni une fonction ni un tableau appelable.")   

        else: # on doit voir car c'es pas bon ya des bugg qui peuvent nous echaper.
            return "booleen"     




















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
        message = f"Parseur → {message}"
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
        declaration: list[Declaration] = self.parse_declaration()
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
        # ✅ Déléguer le type de la constante à l'analyseur sémantique
        return DeclarationConstante(nom, valeur, None)

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
        if self.token_courant()["type"] != "PAREN_FERMANT":
            les_arguments.append(self.parse_expression())
            while self.token_courant()["type"] == "separateur":
                self.consommer("separateur")
                les_arguments.append(self.parse_expression())

        self.consommer("PAREN_FERMANT")
        return les_arguments

    def obtenir_type_expression(self, expr: Expression, est_tableau: bool = False) -> str:
        if not est_tableau :
            if isinstance(expr , Nombre) :
                return "entier" if isinstance(expr.valeur, int) else "reel"
            elif isinstance(expr, Caractere):
                return "caractere"
            elif isinstance(expr, ChaineCaractere):
                return "chaine"
            elif isinstance(expr, Booleen):
                return "booleen"
            elif isinstance(expr, OperationBinaire):
                type_g = self.obtenir_type_expression(expr.gauche)
                type_d = self.obtenir_type_expression(expr.droite)
                if expr.operateur in ("+", "-", "*", "/", "div", "mod", "^"):
                    return "reel" if "reel" in (type_g, type_d) or expr.operateur == "/" else "entier"
                elif expr.operateur in ("=", "<>", "<", ">", "<=", ">=", "et", "ou"):
                    return "booleen"
            elif isinstance(expr, OperationUnaire):
                if expr.operateur == "non":
                    return "booleen"
                return self.obtenir_type_expression(expr.operande)
            else:
                self.erreur("Erreur interne.")
        else:
            if isinstance(expr, list) and len(expr) > 0:
                premier_type = self.obtenir_type_expression(expr[0])
                for element in expr :
                    if self.obtenir_type_expression(element) != premier_type :
                        self.erreur("Tous les éléments d'un tableau doivent avoir le même type.")
                return premier_type
            self.erreur("Erreur interne.")


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
