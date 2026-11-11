#FICHIER EXTERNES
from AVANT_TOUS.avant_lexer import main as avant_lexer
from LEXER.lexer import main as lexer
from PARSEUR.parseur import Parseur
from UTILS.afficher_ast import afficher_ast
from SEMANTIQUE.analyseur_semantique import AnalyseurSemantique
from INTERPRETEUR.interpreteur import Interpreteur
from UTILS.erreur import erreur

#FICHIER PYTHON
import pprint as p
import sys

"""LANGAGE EVA"""
try:
    code_source: str
    fichier_json: dict
    code_source, fichier_json = avant_lexer()

    original_code_source: str = code_source

    token: list[dict] = lexer(code_source, fichier_json)
    parseur = Parseur(token)
    ast = parseur.parse_programme()
    ANA_SEMAN = AnalyseurSemantique(ast)
    ANA_SEMAN.visiter_algorithme()
    interprete = Interpreteur()
    interprete.interpreter(ast)

except KeyboardInterrupt:
    print("\n\033[1m\033[93mArrêt en cours... // Stopping...\033[0m")
    sys.exit(130)

except RecursionError:
    erreur(
        "Profondeur de récursivité maximale dépassée. "
        "Vérifiez que votre fonction a un cas de base // "
        "Maximum recursion depth exceeded. "
        "Check that your function has a base case 🚫"
    )
