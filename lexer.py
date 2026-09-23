from aide_lexer import *
from erreur import aide_remonter
from tous_les_types import Token, Langage


def main(code_source: str, le_json: Langage) -> list[Token]:
    token: list[Token] = []
    ligne: int = 1
    index: int = 0

    _commentaire: list[str] = le_json["commentaire"]
    cas_symbole: list[str] = ["=", "<", ">", "+", "-", "*", "/", "^", "←", ":", ","]

    while index < len(code_source):
        caractere: str = code_source[index]

        if caractere in (" ", "\t"):
            ligne, index = espace(ligne, index)

        elif caractere == "\n":
            ligne, index = retour_ligne(ligne, index)

        elif caractere in _commentaire:
            ligne, index = commentaire(ligne, index, code_source, _commentaire)

        elif caractere == "'":
            ligne, index = un_seul_caractere(ligne, index, code_source, token)

        elif caractere == '"':
            ligne, index = chaine_caractere(ligne, index, code_source, token)

        elif caractere in ("(", ")"):
            ligne, index = parenthese(ligne, index, code_source, token)

        elif caractere.isdigit():
            ligne, index = numerique(ligne, index, code_source, token)

        elif caractere in cas_symbole:
            ligne, index = symbole(ligne, index, code_source, token, le_json)

        elif caractere.isalpha() or caractere == "_":
            ligne, index = alpha(ligne, index, code_source, token, le_json)

        else:
            aide_remonter(index, code_source, ligne,
                          f"Terme non pris en charge : '{caractere}' // Unsupported token: '{caractere}' 🚫")

    token_append("FIN_FICHIER", None, ligne, token)
    return token


if __name__ == "__main__":
    main()
