from avant_lexer import main as avant_lexer

"""LANGAGE EVA """
code_source: str
fichier_json: dict
code_source, fichier_json = avant_lexer()
print(code_source)
print(fichier_json)
