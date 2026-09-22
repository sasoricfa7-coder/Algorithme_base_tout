from aide_lexer import *
from erreur import gestion as erreur
from tous_les_types import Token, Langage

def main(code_source: str, le_json: Langage) -> list[Token] :
    token: list[Token] = []
    ligne: int = 1
    colonne: int = 1
    index: int = 0

    _commentaire: list[str] = le_json["commentaire"]
    cas_symbole: list[str] = [ "=", "<", ">", "<=", ">=", "<>", "+", "-", "*", "/", "^", "←", ":", ","]

    while (index < len(code_source)) :
        caractere: str = code_source[index]

        if caractere in (" ", "\t") :
            ligne, colonne, index = espace(ligne, colonne, index)

        elif caractere == "\n" :
            ligne, colonne, index = retour_ligne(ligne, colonne, index)

        elif caractere in _commentaire :
            ligne, colonne, index = commentaire(ligne, colonne, index, code_source, _commentaire)

        elif caractere == "'" :
            ligne, colonne, index = un_seul_caractere(ligne, colonne, index, code_source, token)

        elif caractere == '"' :
            ligne, colonne, index = chaine_caractere(ligne, colonne, index, code_source, token)

        elif caractere in ("(" , ")") :
            ligne, colonne, index = parenthese(ligne, colonne, index, code_source, token)

        elif caractere.isdigit() :
            ligne, colonne, index = numerique(ligne, colonne, index, code_source, token)

        elif caractere in cas_symbole :
            ligne, colonne, index = symbole(ligne, colonne, index, code_source, token, le_json)

        elif caractere.isalpha() or caractere == "_" :
            ligne, colonne, index = alpha(ligne, colonne, index, code_source, token, le_json)

        else :
            aide_remonter(index, code_source, ligne, colonne, "TERMES non pris en charge")

    token_append("FIN_FICHIER", None, ligne, colonne, 0, token)

    return token

if __name__=="__main__" :
    main()
