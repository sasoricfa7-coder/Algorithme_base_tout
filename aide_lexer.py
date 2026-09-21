from erreur import gestion as erreur
import unicodedata
from tous_les_types import Token, Langage

def index_Error(code_source, index) -> bool:
    if index < len(code_source) :
        return True
    return False

#---------------------------------------------------------------------------------------------
def espace(ligne: int, colonne: int, index: int) -> tuple[int, int, int]:
    return ligne, colonne + 1 , index + 1
#---------------------------------------------------------------------------------------------
def retour_ligne(ligne: int, colonne: int, index: int) -> tuple[int, int, int] :
    return ligne + 1 , 1, index + 1
#---------------------------------------------------------------------------------------------
def commentaire (ligne: int, colonne: int, index: int, code_source: str, _commentaire: list[str]) -> tuple[int, int, int] :
    index += 1
    colonne += 1
    while ( index_Error(code_source, index) and  (code_source[index] not in _commentaire)) :
        index += 1
        if len(code_source) > index and code_source[index] == "\n" :
            ligne += 1
            colonne = 1
        else :
            colonne += 1

    if index_Error(code_source, index) and code_source[index] not in _commentaire :
        aide_remonter(index, code_source, ligne, colonne, "A la fin du ficher vous avez oublier de fermer le bloc de commentaire")
    return ligne, colonne, index
#---------------------------------------------------------------------------------------------
def token_append(type_: str, valeur: str | int | float | None, ligne: int, colonne: int, longueur: int, token: list[Token]) -> None: # valeur
    # peut être int ou float j'en ai conscience
    token.append({
        "type" : type_,
        "valeur" : valeur,
        "ligne" : ligne,
        "colonne" : colonne,
        "longueur" : longueur,
    })
#---------------------------------------------------------------------------------------------
def aide_remonter(index: int, code_source: str, ligne: int, colonne: int, message: str) -> None:
    ligne_depart: int = ligne
    colonne_depart: int = colonne
    contenu: str = ""
    index_depart: int = index
    while (index_Error(code_source, index) and (code_source[index] != "\n") and (ligne_depart != 1) ):
        index -= 1
    if ligne != 1 :
        for i in range( (index_depart - index) ) :
            contenu += code_source[index + i]
    else :
        message = f"A la première ligne : {message}"

    erreur(message, ligne_depart, colonne_depart, contenu)


def un_seul_caractere(ligne: int, colonne: int, index: int, code_source: str, token: list[Token]) -> tuple[int, int, int]:
    ligne_depart: int = ligne
    colonne_depart: int = colonne
    index += 1
    colonne += 1

    if not index_Error(code_source, index) :
        aide_remonter(index, code_source, ligne, colonne, "Fichier mal terminer veuillez inspecter la dernière ligne")

    if (index_Error(code_source, index) and  code_source[(index + 1)] != "'") :
        aide_remonter(index, code_source, ligne, colonne, "Entre deux apostrofes '' il ne dois avoir qu'un seul caractère")

    token_append("CARACTERE", code_source[index], ligne_depart, colonne_depart, 1, token)
    index += 2
    colonne += 2

    return ligne, colonne, index
#---------------------------------------------------------------------------------------------
def chaine_caractere (ligne: int, colonne: int, index: int, code_source: str, token: list[Token]) -> tuple[int, int, int]:
    ligne_depart: int = ligne
    colonne_depart: int = colonne

    if not index_Error(code_source, index) :
        aide_remonter(index, code_source, ligne, colonne, "Fichier mal terminer veuillez inspecter la dernière ligne")
    
    index += 1
    depart = index
    colonne += 1

    while ( index_Error(code_source, index) and  code_source[index] != '"' and code_source[index] != "\n") :
        index += 1
        colonne += 1

    if  (index_Error(code_source, index) and  code_source[index] != '"' ):
        aide_remonter(index, code_source, ligne, colonne, "Chaine n'est pas fermée")
    if not index_Error(code_source, index) :
        aide_remonter(index, code_source, ligne, colonne, "Fin de fichier anormal")

    valeur: str = code_source[depart : index]
    index += 1
    colonne += 1

    token_append("CHAINE_CARACTERE", valeur, ligne_depart, colonne_depart, len(valeur), token)
    return ligne, colonne, index
#---------------------------------------------------------------------------------------------
def parenthese (ligne: int, colonne: int, index: int, code_source: str, token: list[Token]) -> tuple[int, int, int]:
    type_: str = "PAREN_OUVRANT" if code_source[index] == "(" else "PAREN_FERMANT"
    token_append(type_, code_source[index], ligne, colonne, 1, token)

    index += 1
    colonne += 1

    return ligne, colonne, index
#---------------------------------------------------------------------------------------------
def numerique (ligne: int, colonne: int, index: int, code_source: str, token: list[Token]) -> tuple[int, int, int]:
    depart: int = index
    point_utiliser: bool = False
    colonne_depart: int = colonne

    while (
         index_Error(code_source, index) and
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

    if not code_source[index - 1].isdigit() :
        aide_remonter(index, code_source, ligne, colonne, "Les nombres doivent être soit réels ou entiers et sur une même ligne.")

    valeur = int(code_source[depart : index]) if not point_utiliser else float(code_source[depart : index])
    token_append("NOMBRE", valeur, ligne, colonne_depart, len(code_source[depart : index]), token)  
    return ligne, colonne, index    
     
#---------------------------------------------------------------------------------------------
def sans_accents(texte: str) -> str:
    # 1. Décompose : "É" -> "E" + "´" (accent combinant)
    decompose = unicodedata.normalize("NFD", texte)
    # 2. Garde tout sauf les accents (catégorie "Mn" = Mark, nonspacing)
    sans = "".join(c for c in decompose if unicodedata.category(c) != "Mn")
    # 3. Met en minuscules (optionnel)
    return sans.lower()
#---------------------------------------------------------------------------------------------
def symbole(ligne: int, colonne: int, index: int, code_source: str, token: list[Token], fichier: Langage) -> tuple[int, int, int]:
    valeur_un: str = code_source[index]
    depart = index
    index += 1
    if index_Error(code_source, index)  :
        valeur_deux = valeur_un + code_source[index]
        valide: bool
        type_ : str
        valide, type_ = verificateur(valeur_deux, fichier)
        valeur_final : str = valeur_deux
        if not valide :
            valide, type_ = verificateur(valeur_un, fichier)
            valeur_final = valeur_un
        else :
            index += 1
        token_append(type_, valeur_final, ligne, colonne, len(code_source[depart : index]), token)
        return ligne, colonne + (index - depart), index
    else :
        aide_remonter(index, code_source, ligne, colonne, "vers la fin symbole seul ne sert à rien")
#---------------------------------------------------------------------------------------------

def verificateur(valeur: str, le_json: Langage) -> (bool, str): # J'ai separer ca la en cas de modification du langage seul celui ci change
    # Je sais qu'arriver au parseur je vais remodifier le json pour me faciliter la tâche donc je reviendrai sur cette fonction
    valide: bool = True
    type_: str = "identifiant"
    if valeur in le_json["mots_cles_simple"] :
        type_ = "mots_cles_simple"

    elif valeur in le_json["les_mots_ambigu"] :
        type_ = "les_mots_ambigu"

    elif valeur in le_json["operateurs_logiques"] :
        type_ = "operateurs_logiques"

    elif valeur in le_json["operateurs_comparaison"] :
        type_ = "operateurs_comparaison"

    elif valeur in le_json["operateurs_arihmetiques"] :
        type_ = "operateurs_arihmetiques"

    elif valeur in le_json["valeur_booleen"] :
        type_ = "valeur_booleen"

    elif valeur in le_json["operateurs_affectation"] :
        type_ = "operateurs_affectation"

    elif valeur in le_json["autres"] :
        type_ = "autres"

    else :
        valide = False

    return valide, type_
    
#---------------------------------------------------------------------------------------------
def alpha (ligne: int, colonne: int, index: int, code_source: str, token: list[Token], fichier: Langage) -> tuple[int, int, int]:
    depart: int = index
    colonne_depart: int = colonne

    while (
        index_Error(code_source, index) and
        (
            code_source[index].isalpha() or
            code_source[index] == "_"
        )
    ) :
        index += 1
        colonne += 1

    valide: bool
    type_ : str = "identifiant"
    vrai_valeur_un = code_source[depart : index]
    valeur_un: str = sans_accents(vrai_valeur_un)
    valide, type_ = verificateur(valeur_un, fichier)
    valeur_final: str = vrai_valeur_un

    avant: int = index
    while (
        index_Error(code_source, index) and
        code_source[index] in (" ", "\t")
    ) :
        index += 1
        colonne += 1
        
    depart_2: int = index
    if len(code_source) > index and code_source[index].isalpha() :
        while(
            index_Error(code_source, index) and
            (
                code_source[index].isalpha() or
                code_source[index] == "_"
            )
        ) :
            index += 1
            colonne += 1
        vrai_valeur_deux = code_source[depart_2 : index]
        valeur_deux = sans_accents(vrai_valeur_deux)
        valide, type_ = verificateur(f"{valeur_un} {valeur_deux}", fichier)
        if not valide :
            type_ = "identifiant"
            index = index - (index - avant)
            colonne = colonne - (index - avant)
            valeur_final = vrai_valeur_un
        else :
            valeur_final = f"{vrai_valeur_un} {vrai_valeur_deux}"

    
    token_append(type_, valeur_final, ligne, colonne_depart, len(code_source[depart : index]), token)
    return ligne, colonne, index
