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

    if (index >= len(code_source)) and (code_source[index] not in _commentaire) :
        aide_remonter(index, code_source, ligne, colonne, "A la fin du ficher vous avez oublier de fermer le bloc de commentaire")
    return ligne, colonne, index
#---------------------------------------------------------------------------------------------
def token_append(type_: str, valeur, ligne: int, colonne: int, longueur: int, token: list[dict) :
    token.append({
        "type" : type_,
        "valeur" : valeur,
        "ligne" : ligne,
        "colonne" : colonne,
        "longueur" : longueur,
    })
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

    token_append("CARACTERE", code_source[index], ligne_depart, colonne_depart, 1, token)
    index += 2
    colonne += 2

    return ligne, colonne, index
#---------------------------------------------------------------------------------------------
def chaine_caractere (ligne: int, colonne: int, index: int, code_source: str, token: list[dict]) :
    ligne_depart: int, colonne_depart: int = ligne, colonne

    if (index + 1) >= len(code_source) :
        aide_remonter(index, code_source, ligne, colonne, "Fichier mal terminer veuillez inspecter la dernière ligne")
    
    index += 1
    depart = index
    colonne += 1

    while (code_source[index] != '"' and len(code_source) > index and code_source[index] != "\n") :
        index += 1
        colonne += 1

    if code_source[index] != '"' :
        aide_remonter(index, code_source, ligne, colonne, "Chaine n'est pas fermée")
    if code_source[index] >= len(code_source) :
        aide_remonter(index, code_source, ligne, colonne, "Fin de fichier anormal")

    valeur: str = code_source[depart : index]
    index += 1
    colonne += 1

    token_append("CHAINE_CARACTERE", valeur, ligne_depart, colonne_depart, len(valeur), token)
    return ligne, colonne, index
#---------------------------------------------------------------------------------------------
def parenthese (ligne: int, colonne: int, index: int, code_source: str, token: list[dict]) :
    type_: str = "PAREN_OUVRANT" if code_source[index] == "(" else "PAREN_FERMANT"
    token_append(type_, code_source[index], ligne, colonne, 1, token)

    index += 1
    colonne += 1

    return ligne, colonne, index
#---------------------------------------------------------------------------------------------
def numerique (ligne: int, colonne: int, index: int, code_source: str, token: list[dict]) :
    depart: int = index
    point_utiliser: bool = False
    colonne_depart: int = colonne_depart

    while (
         (index < len(code_source)) and
         (
            (code_source[index].isdigit()) or
            (code_source[index] == "." and not point_utiliser)
         ) and
         (code_source[index] != "\n")
    ) :
        if code_source[index] == "." :
            point_utiliser = True
        index += 1
        colonne += 1

    if not code_source[index - 1].isdigit :
        aide_remonter(index, code_source, ligne, colonne, "Les nombres doivent être soit réels ou entiers et sur une même ligne.")

    valeur = int(code_source[depart : index]) if not point_utiliser else float(code_source[depart : index])
    token_append("NOMBRE", valeur, ligne, colonne_depart, len(code_source[depart : index]), token)       
#---------------------------------------------------------------------------------------------
def alpha (ligne: int, colonne: int, index: int, code_source: str, token: list[dict]) :
    
