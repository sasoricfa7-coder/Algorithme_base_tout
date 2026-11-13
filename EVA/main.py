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

#FICHIER EXTERNES
from AVANT_TOUS.avant_lexer import main as avant_lexer
from LEXER.lexer import main as lexer
from PARSEUR.parseur import Parseur
from SEMANTIQUE.analyseur_semantique import AnalyseurSemantique
from INTERPRETEUR.interpreteur import Interpreteur
from UTILS.erreur import erreur

#FICHIER PYTHON
import sys

def stopper(n: int = 1):
    sys.exit(n)

"""LANGAGE EVA"""
try:

    #CHARGEMENT DU CODE SOURCE 
    code_source, fichier_json = avant_lexer()

    #FORMATION DES TOKENS PAR LE LEXER
    token: list[dict] = lexer(code_source, fichier_json)

    #FORMATION DE L'AST PAR LE PARSEUR
    ast = Parseur(token).ast

    #VERIFICATION DE L'AST PAR L'ANALYSEUR SEMATIQUE
    ANA_SEMAN = AnalyseurSemantique(ast)

    #INTERPRÉTATION
    interprete = Interpreteur(AST = ast)

except KeyboardInterrupt:
    print("\n\033[1m\033[93mArrêt en cours... // Stopping...\033[0m")
    stopper(130)

except RecursionError:
    erreur(
        "Profondeur de récursivité maximale dépassée. "
        "Vérifiez que votre fonction a un cas de base // "
        "Maximum recursion depth exceeded. "
        "Check that your function has a base case 🚫"
    )

except PermissionError:
    erreur(
        "Vous n'avez pas la permission d'executer ce fichier"
    )
