from avant_lexer import main as avant_lexer
from lexer import main as lexer
from tous_les_types import Parseur, afficher_ast, AnalyseurSemantique
import pprint as p
from interpreteur import Interpreteur
import sys
from erreur import erreur

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
