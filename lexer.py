from aide_lexer import *

def main(code_source: str, le_json: dict) -> list[dict] :
    token: list[dict] = []
    ligne: int = 1
    colonne: int = 1
    index: int = 0

    _commentaire: dict[str, str] = le_json["commentaire"]

    while (index < len(code_source)) :
        caractere: str = code_source[index]

        if caractere in (" ", "\t") :
            ligne, colonne, index = espace(ligne, colonne, index)
            continue

        if caractere == "\n" :
            ligne, colonne, index = retour_ligne(ligne, colonne, index)
            continue

        if caractere in _commentaire :
            ligne, colonne, index = commentaire(ligne, colonne, index, code_source, _commentaire)
            continue

        if caractere == "'" :
            ligne, colonne, index = un_seul_caractere(ligne, colonne, index, code_source, token)
            continue

        if caractere == '"' :
            ligne, colonne, index = chaine_caractere(ligne, colonne, index, code_source, token)
            continue

        if caractere in ("(" , ")") :
            ligne, colonne, index = parenthese(ligne, colonne, index, code_source, token)
            continue

        if caractere.isdigit() :
            ligne, colonne, index = numerique(ligne, colonne, index, code_source, token)
            continue

        if caractere.isalpha() or caractere == "_" :
            ligne, colonne, index = alpha(ligne, colonne, index, code_source, token, le_json)
            continue

        token_append("FIN_FICHIER", None, ligne + 1, colonne + 1, 0, token)

        return token

if __name__=="__main__" :
    main()
