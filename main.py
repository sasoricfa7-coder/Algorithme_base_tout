from avant_lexer import main as avant_lexer
from lexer import main as lexer
#from tous_les_types import Parseur, afficher_ast
import pprint as p

"""LANGAGE EVA"""
code_source: str
fichier_json: dict
code_source, fichier_json = avant_lexer()

original_code_source: str = code_source

token: list[dict] = lexer(code_source, fichier_json)
p.pprint(token)
"""parseur = Parseur(token)
ast = parseur.parse_programme()
afficher_ast(ast)"""
