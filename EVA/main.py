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
