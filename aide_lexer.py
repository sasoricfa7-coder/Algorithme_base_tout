from erreur import gestion as erreur


#---------------------------------------------------------------------------------------------
def espace(ligne: int, colonne: int, index: int) -> (int, int, int):
    return ligne, colonne + 1 , index + 1
#---------------------------------------------------------------------------------------------
def retour_ligne(ligne: int, colonne: int, index: int) -> (int, int, int) :
    return ligne + 1 , 1, index + 1
#---------------------------------------------------------------------------------------------
def commentaire (ligne: int, colonne: int, index: int, code_source: str, _commentaire: dict) -> (int, int, int) :
    index += 1
    colonne += 1
    while ( (code_source[index] not in _commentaire) and (index < len(code_source)) ) :
        index += 1
        if code_source[index] == "\n" :
            ligne += 1
            colonne = 1
        else :
            colonne += 1

    if (index == len(code_source)) and (code_source[index] not in _commentaire) :
        erreur("A la fin du ficher vous avez oublier de fermer le bloc de commentaire")
    return ligne, colonne, index
#---------------------------------------------------------------------------------------------
def aide_remonter(index: int, code_source: str, ligne: int, colonne: int, message: str) :
    ligne_depart: int, colonne_depart: int = ligne, colonne
    contenu: str = ""
    index_depart: int = index
    while (code_source[index] != "\n") and (ligne_depart != 1):
        index -= 1
    if ligne != 1 :
        for i in range( (index_depart - index) ) :
            contenu += code_source[index + i]
    else :
        message = "A la première ligne"

    erreur(message, ligne_depart, colonne_depart, contenu)


def un_seul_caractere(ligne: int, colonne: int, index: int, code_source: str, token: list[dict]) :
    ligne_depart: int, colonne_depart: int = ligne, colonne
    index += 1
    colonne += 1

    if (index + 1) >= len(code_source) :
        aide_remonter(index, code_source, ligne, colonne, "Fichier mal terminer veuillez inspecter la dernière ligne")

    if (index + 1) != "'" :
        aide_remonter(index, code_source, ligne, colonne, "Entre deux apostrofes '' il ne dois avoir qu'un seul caractère")
