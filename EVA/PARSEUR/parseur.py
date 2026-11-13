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

from UTILS.erreur import erreur
from TYPES_CREER.__parseur import *
from TYPES_CREER.__lexer import Token


#------------PARSEUR-------------------------------------------
class Parseur:
    def __init__(self, tokens: list[Token]) -> None :
        self.tokens: list[Token] = tokens
        self.position: int = 0
        self.ast: Algorithme = self.parse_programme()

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

    def erreur(self, message, ligne: int | None = None) -> None:
        message = f"Parseur → {message}"
        if ligne is None:
            ligne = self.tokens[self.position]["ligne"]
        erreur(message, ligne)

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

        return Algorithme(self.tokens[index_nom]["valeur"], Fonction_bloc, Procedure_bloc, declaration, corps_complet, self.tokens[index_nom]["ligne"] )

    def parse_fonction(self) -> Fonction:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "fonction")
        nom: str = str(self.token_courant()["valeur"])
        self.consommer("identifiant")
        parametre: list[Parametre] = self.parse_parametres()
        self.consommer("declaration_type")
        
        retour_est_tableau = False
        if self.token_courant()["valeur"] == "tableau":
            retour_est_tableau = True
            self.consommer("mots_cles", "tableau")
        
        type_retour: str = str(self.token_courant()["valeur"])
        if type_retour not in LES_TYPES_PRIS :
            self.erreur(f"Type de retour '{type_retour}' non pris en charge.")
            
        self.consommer("mots_cles")
        declaration: list[Declaration] = self.parse_declaration()
        corps_complet: list[Instruction] = self.parse_corps()
    
        return Fonction(nom, parametre, type_retour, declaration, corps_complet, retour_est_tableau, token_debut["ligne"])

    def parse_procedure(self) -> Procedure:
        token_debut = self.token_courant()
        self.consommer( "mots_cles","procedure")
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        parametre: list[Parametre] = self.parse_parametres()
        declaration: list[Declaration] = self.parse_declaration()
        corps_complet: list[Instruction] = self.parse_corps()

        return Procedure(nom, parametre, declaration, corps_complet, token_debut["ligne"])

    def parse_aide_parametre(self) -> Parametre:
        token_debut = self.token_courant()
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("declaration_type")
        
        est_tableau = False
        if self.token_courant()["valeur"] == "tableau":
            est_tableau = True
            self.consommer("mots_cles", "tableau")
        
        le_type: str = self.token_courant()["valeur"]
        if self.token_courant()["valeur"] not in LES_TYPES_PRIS :
            self.erreur(f"{self.token_courant()['valeur']} type non pris en charge.", token_debut["ligne"])
        self.consommer("mots_cles")
    
        return Parametre(nom, le_type, est_tableau)

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
        token_debut = self.token_courant()
        Variable_bloc: list[DeclarationVariable] = []
        Constante_bloc: list[DeclarationConstante] = []
        
        vus: set[str] = set()
        while self.token_courant()["valeur"] in ("variable", "constante") :
            mot = self.token_courant()["valeur"]
            if mot in vus :
                self.erreur(f'Bloc "{mot}" déjà déclaré // "{mot}" block already declared 🚫', token_debut["ligne"])    
            vus.add(mot)
            if mot == "variable" :
                Variable_bloc += self.parse_bloc_variables()
            else :
                Constante_bloc += self.parse_bloc_constantes()
        return Variable_bloc + Constante_bloc

    def parse_bloc_constantes(self) -> list[Declaration]:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "constante")
        resultats: list[Declaration] = []
        while self.token_courant()["valeur"] == "tableau" or self.token_courant()["type"] == "identifiant" :
            if self.token_courant()["valeur"] == "tableau" :
                resultats.append(self.aide_constante_tableau())
            else :
                resultats.append(self.parse_aide_constante())

        if not resultats:
            self.erreur("Un bloc 'constante' doit contenir au moins une déclaration 🚫", token_debut["ligne"])

        return resultats

    def parse_aide_constante(self) -> DeclarationConstante:
        token_debut = self.token_courant()
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("operateurs_affectation")
        valeur: Expression = self.parse_expression()

        self.fin_de_ligne()
        # ✅ Déléguer le type de la constante à l'analyseur sémantique
        return DeclarationConstante(nom, valeur, None, token_debut["ligne"])

    def aide_constante_tableau(self) -> DeclarationTableau:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "tableau")
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("operateurs_affectation")
        les_arguments = self.parse_arguments()

        self.fin_de_ligne()
        return DeclarationTableau(nom, None, None, les_arguments, token_debut["ligne"])
        

    def parse_bloc_variables(self) -> list[Declaration]:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "variable")
        resultats: list[Declaration] = []
        while self.token_courant()["valeur"] == "tableau" or self.token_courant()["type"] == "identifiant" :
            if self.token_courant()["valeur"] == "tableau" :
                resultats += self.parse_aide_tableau()
            else :
                resultats.extend(self.parse_aide_variable())

        if not resultats:
            self.erreur("Un bloc 'variable' doit contenir au moins une déclaration 🚫", token_debut["ligne"])

        return resultats

    def parse_aide_variable(self) -> list[DeclarationVariable]:
        token_debut = self.token_courant()
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
            self.erreur(f"{type_} non pris en charge dans le langage EVA", token_debut["ligne"])
        self.consommer("mots_cles")
        
        return [DeclarationVariable(nom, type_, token_debut["ligne"]) for nom in noms]

    def parse_aide_tableau(self) -> list[Declaration]:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "tableau")
        
        tableaux: list[tuple[str, list[Expression]]] = []
        
        # 1. Premier tableau
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("PAREN_OUVRANT")
        dimensions: list[Expression] = [self.parse_expression()]
        if self.token_courant()["type"] == "separateur":
            self.consommer("separateur")
            dimensions.append(self.parse_expression())
        self.consommer("PAREN_FERMANT")
        
        nb_dim = len(dimensions)
        tableaux.append((nom, dimensions))
        
        # 2. Tableaux suivants
        while self.token_courant()["type"] == "separateur":
            self.consommer("separateur")
            
            # On s'attend obligatoirement à un autre tableau
            if self.token_courant()["type"] == "identifiant" and self.token_suivant()["type"] == "PAREN_OUVRANT":
                nom2: str = self.token_courant()["valeur"]
                self.consommer("identifiant")
                self.consommer("PAREN_OUVRANT")
                dims2: list[Expression] = [self.parse_expression()]
                if self.token_courant()["type"] == "separateur":
                    self.consommer("separateur")
                    dims2.append(self.parse_expression())
                self.consommer("PAREN_FERMANT")
                
                # ✅ Vérification de la dimension avec message détaillé
                if len(dims2) != nb_dim:
                    self.erreur(
                        f"Impossible de mélanger des dimensions différentes : "
                        f"le tableau '{nom}' est en {nb_dim}D, "
                        f"mais '{nom2}' est en {len(dims2)}D. "
                        f"Tous les tableaux d'une même ligne doivent avoir la même dimension. 🚫",
                        token_debut["ligne"],
                    )
                
                tableaux.append((nom2, dims2))
            else:
                # ✅ Si ce n'est pas un tableau, on bloque avec message détaillé
                val = self.token_courant()["valeur"]
                self.erreur(
                    f"Impossible de mélanger tableaux et variables : "
                    f"le tableau '{nom}' ne peut pas être déclaré sur la même ligne que '{val}'. "
                    f"Déclarez les tableaux et les variables sur des lignes séparées. 🚫",
                    token_debut["ligne"],
                )

        # 3. Le type commun
        self.consommer("declaration_type")
        type_: str = self.token_courant()["valeur"]
        if type_ not in LES_TYPES_PRIS:
            self.erreur(f"{type_} non pris en charge dans le langage EVA", token_debut["ligne"])
        self.consommer("mots_cles")

        # 4. On construit le résultat
        resultats: list[Declaration] = []
        for t_nom, t_dims in tableaux:
            resultats.append(DeclarationTableau(nom=t_nom, type=type_, dimensions=t_dims, ligne=token_debut["ligne"]))

        return resultats

    def parse_instructions(self) -> list[Instruction]:
        resultats: list[Instruction] = []
        while not self.est_fin_bloc():
            resultats.append(self.parse_instruction())
            self.fin_de_ligne()
        return resultats

    def parse_corps(self) : # Lui ne gère que les cas ou on est entourer debut ... fin
        self.consommer("mots_cles", "debut")
        corps: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "fin")
        return corps

    def parse_affectation(self) -> Affectation:
        token_debut = self.token_courant()
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("operateurs_affectation")
        retour: Expression = self.parse_expression()
        return Affectation(Identifiant(nom, token_debut["ligne"]), retour, token_debut["ligne"])

    def parse_instruction(self) -> Instruction :
        token_debut = self.token_courant()
        if token_debut["type"] == "identifiant" :
            if self.token_suivant()["type"] == "operateurs_affectation" :
                return self.parse_affectation()
            elif (self.token_suivant()["type"] == "PAREN_OUVRANT") :
                nom: str = token_debut["valeur"]
                self.consommer("identifiant")
                les_arguments = self.parse_arguments()
                if self.token_courant()["type"] == "operateurs_affectation" :
                    self.consommer("operateurs_affectation")
                    retour: Expression = self.parse_expression()
                    return Affectation(Indexation(nom, les_arguments, token_debut["ligne"]), retour, token_debut["ligne"])
                else :
                    return AppelInstruction(nom, les_arguments, token_debut["ligne"])
            else :
                self.erreur("Instruction invalide : identifiant tout seul", token_debut["ligne"])
        else :
            match token_debut["valeur"] :
                case "ecrire" : return self.parse_ecrire()
                case "lire" : return self.parse_lire()
                case "si" : return self.parse_si()
                case "cas": return self.parse_cas()
                case "pour": return self.parse_pour()
                case "tant que" : return self.parse_tant_que()
                case "repeter" : return self.parse_repeter()
                case "retourne" : return self.parse_retourne()
                case _ : self.erreur("voici ce qui était attendu : Identifiant | un mots clé", token_debut["ligne"])

    def parse_ecrire(self) -> Ecrire:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "ecrire")
        return Ecrire(self.parse_arguments(), token_debut["ligne"])

    def parse_cible(self) -> Identifiant | Indexation:
        token_debut = self.token_courant()
        nom: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        if self.token_courant()["type"] == "PAREN_OUVRANT" :
            indices = self.parse_arguments()
            return Indexation(nom, indices, token_debut["ligne"])
        return Identifiant(nom, token_debut["ligne"])

    def parse_lire(self) -> Lire:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "lire")
        self.consommer("PAREN_OUVRANT")
        cibles: list[Identifiant | Indexation] = []
        cibles.append(self.parse_cible())
        while self.token_courant()["type"] == "separateur" :
            self.consommer("separateur")
            cibles.append(self.parse_cible())
        self.consommer("PAREN_FERMANT")
        return Lire(cibles, token_debut["ligne"])
        
    def parse_si(self) -> Si:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "si")
        condition: Expression = self.parse_expression()
        self.consommer("mots_cles", "alors")
        alors: list[Instruction] = self.parse_instructions()
        sinon: list[Instruction] = []
        if self.token_courant()["valeur"] == "sinon" :
            self.consommer("mots_cles", "sinon")
            sinon = self.parse_instructions()
        self.consommer("mots_cles", "fin si")
        return Si(condition, alors, sinon, token_debut["ligne"])

    def parse_branche_cas(self) -> BrancheCas:
        token_debut = self.token_courant()
        valeur: Expression = self.parse_expression()
        self.consommer("declaration_type")
        if self.token_courant()["valeur"] in ("si", "cas", "pour", "tant que", "repeter") :
            self.erreur("Un bloc ne peut pas tenir sur une ligne dans un Cas : entourer le dans un debut ... fin", token_debut["ligne"])

        corps: list[Instruction] = []
        if self.token_courant()["valeur"] == "debut" :
            corps = self.parse_corps()
            if len(corps) < 2:
                self.erreur(
                    "Utilisation inutile de 'debut ... fin' : "
                    "un bloc 'debut ... fin' dans un cas doit contenir au moins 2 instructions. "
                    "Pour une seule instruction, écrivez-la directement sur la ligne.",
                    token_debut["ligne"],
                )
        else :
            corps = [self.parse_instruction()]
            self.fin_de_ligne()
        return BrancheCas(valeur, corps, token_debut["ligne"])

    def parse_cas(self) -> Cas:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "cas")
        nom: Identifiant | Indexation = self.parse_cible()
        self.consommer("mots_cles", "vaut")
        les_branches: list[BrancheCas] = []
        while self.token_courant()["valeur"] not in ("fin cas", "sinon") :
            les_branches.append(self.parse_branche_cas())
            
        if self.token_courant()["valeur"] != "sinon" :
            self.erreur("Le Sinon est obligatoire dans Cas", token_debut["ligne"])
            
        self.consommer("mots_cles", "sinon")
        self.consommer("declaration_type")
        sinon: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "fin cas")
        return Cas(nom, les_branches, sinon, token_debut["ligne"])

    def parse_pour(self) -> Pour:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "pour")
        indice: str = self.token_courant()["valeur"]
        self.consommer("identifiant")
        self.consommer("operateurs_affectation")
        debut: Expression = self.parse_expression()
        self.consommer("identifiant", "a")
        fin: Expression = self.parse_expression()
        self.consommer("mots_cles", "pas")
        pas: Expression = self.parse_expression()
        self.consommer("mots_cles", "faire")
        corps: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "fin pour")
        return Pour(Identifiant(indice, token_debut["ligne"]), debut, fin, pas, corps, token_debut["ligne"])

    def parse_tant_que(self) -> TantQue:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "tant que")
        condition: Expression = self.parse_expression()
        self.consommer("mots_cles","faire")
        corps: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "fin tant que")
        return TantQue(condition, corps, token_debut["ligne"])

    def parse_repeter(self) -> Repeter:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "repeter")
        corps: list[Instruction] = self.parse_instructions()
        self.consommer("mots_cles", "jusqu'a")
        condition: Expression = self.parse_expression()
        return Repeter(corps, condition, token_debut["ligne"])

    def parse_retourne(self) -> Retourne:
        token_debut = self.token_courant()
        self.consommer("mots_cles", "retourne")
        valeur: Expression = self.parse_expression()
        return Retourne(valeur, token_debut["ligne"])

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

    def parse_expression(self) -> Expression:
        return self.parse_ou_expr()

    def parse_ou_expr(self) :
        token_debut = self.token_courant()
        gauche: Expression = self.parse_et_expr()
        
        while self.token_courant()["type"] == "operateurs_logiques" and self.token_courant()["valeur"] == "ou" :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_logiques", "ou") # je veux rester coherent
            droite: Expression = self.parse_et_expr()
            gauche = OperationBinaire(operateur, gauche, droite, token_debut["ligne"])

        return gauche

    def parse_et_expr(self) -> Expression:
        token_debut = self.token_courant()
        gauche: Expression = self.parse_non_expr()
        
        while  self.token_courant()["type"] == "operateurs_logiques" and self.token_courant()["valeur"] == "et" :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_logiques", "et") # je veux rester coherent
            droite: Expression = self.parse_non_expr()
            gauche = OperationBinaire(operateur, gauche, droite, token_debut["ligne"])

        return gauche

    def parse_non_expr(self) -> Expression:
        token_debut = self.token_courant()
        if  self.token_courant()["type"] == "operateurs_logiques" and self.token_courant()["valeur"] == "non" :
            self.consommer("operateurs_logiques", "non")
            operande: Expression = self.parse_non_expr()
            return OperationUnaire("non", operande, token_debut["ligne"])
        return self.parse_comparaison()

    def parse_comparaison(self) -> Expression:
        token_debut = self.token_courant()
        gauche: Expression = self.parse_additif()
        if self.token_courant()["type"] == "operateurs_comparaison" :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_comparaison")
            droite: Expression = self.parse_additif()
            gauche = OperationBinaire(operateur, gauche, droite, token_debut["ligne"])
        return gauche

    def parse_additif(self) -> Expression:
        token_debut = self.token_courant()
        gauche: Expression = self.parse_multiplicatif()
        while  self.token_courant()["type"] == "operateurs_arihmetiques" and self.token_courant()["valeur"] in ("+", "-") :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_arihmetiques")
            droite: Expression = self.parse_multiplicatif()
            gauche = OperationBinaire(operateur, gauche, droite, token_debut["ligne"])
        return gauche
        
    def parse_multiplicatif(self) -> Expression:
        token_debut = self.token_courant()
        gauche: Expression = self.parse_puissance()
        while  self.token_courant()["type"] == "operateurs_arihmetiques" and self.token_courant()["valeur"] in ("*", "/", "mod", "div") :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_arihmetiques")
            droite: Expression = self.parse_puissance()
            gauche = OperationBinaire(operateur, gauche, droite, token_debut["ligne"])
        return gauche
        
    def parse_puissance(self) -> Expression:
        token_debut = self.token_courant()
        gauche: Expression = self.parse_unaire()
        if  self.token_courant()["type"] == "operateurs_arihmetiques" and self.token_courant()["valeur"] == "^" :
            operateur: str = str(self.token_courant()["valeur"])
            self.consommer("operateurs_arihmetiques", "^")
            droite: Expression = self.parse_puissance()  # Récursion à droite
            return OperationBinaire(operateur, gauche, droite, token_debut["ligne"])
        return gauche
        
    def parse_unaire(self) -> Expression:
        token_debut = self.token_courant()
        if  self.token_courant()["type"] == "operateurs_arihmetiques" and self.token_courant()["valeur"] in ("+", "-") :
            operateur: str = self.token_courant()["valeur"]
            self.consommer("operateurs_arihmetiques")
            operande: Expression = self.parse_unaire()
            return OperationUnaire(operateur, operande, token_debut["ligne"])
        return self.parse_primaire()

    def parse_primaire(self) -> Expression:
        token: Token = self.token_courant()
        type_token: str = token["type"]
        valeur_token = token["valeur"]

        if type_token == "NOMBRE" :
            self.consommer("NOMBRE")
            return Nombre(valeur_token, token["ligne"])
        elif type_token == "CHAINE_CARACTERE" :
            self.consommer("CHAINE_CARACTERE")
            return ChaineCaractere(str(valeur_token), token["ligne"])
        elif type_token == "CARACTERE" :
            self.consommer("CARACTERE")
            return Caractere(str(valeur_token), token["ligne"])
        elif type_token == "valeur_booleen" :
            self.consommer("valeur_booleen")
            return Booleen(valeur_token == "vrai", token["ligne"])
        elif type_token == "identifiant" :
            nom: str = str(valeur_token)
            self.consommer("identifiant")
            if self.token_courant()["type"] == "PAREN_OUVRANT" :
                les_arguments: list[Expression] = self.parse_arguments()
                return AppelFonction(nom, les_arguments, token["ligne"])
            return Identifiant(nom, token["ligne"])
        elif type_token == "PAREN_OUVRANT" :
            self.consommer("PAREN_OUVRANT")
            expr: Expression = self.parse_expression()
            self.consommer("PAREN_FERMANT")
            return expr
        else :
            self.erreur(f"Expression inattendue : token '{type_token}' ({valeur_token})")
