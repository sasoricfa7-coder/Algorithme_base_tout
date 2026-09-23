from erreur import gestion as erreur
import unicodedata
from tous_les_types import Token, Langage, MAX
from utils import sans_accents

def index_Error(code_source: str, index: int) -> bool:
    if index < len(code_source):
        return True
    return False

#---------------------------------------------------------------------------------------------
def espace(ligne: int, index: int) -> tuple[int, int]:
    return ligne, index + 1

#---------------------------------------------------------------------------------------------
def retour_ligne(ligne: int, index: int) -> tuple[int, int]:
    return ligne + 1, index + 1

#---------------------------------------------------------------------------------------------
def commentaire(ligne: int, index: int, code_source: str, _commentaire: list[str]) -> tuple[int, int]:
    index += 1
    ligne_depart = ligne
    while (index_Error(code_source, index) and (code_source[index] not in _commentaire)):
        if code_source[index] == "\n":
            ligne += 1
        index += 1
    
    # ✅ Si on n'a PAS trouvé le délimiteur fermant → erreur
    if not index_Error(code_source, index):
        aide_remonter(index, code_source, ligne_depart,"Bloc de commentaire jamais fermé // Unclosed comment block 🙈")
    
    # ✅ consommer le % fermant
    index += 1
    return ligne, index

#---------------------------------------------------------------------------------------------
def token_append(type_: str, valeur: str | int | float | None, ligne: int, token: list[Token]) -> None:
    token.append({
        "type": type_,
        "valeur": valeur,
        "ligne": ligne,
    })

#---------------------------------------------------------------------------------------------
def aide_remonter(index: int, code_source: str, ligne: int, message: str) -> None:
    ligne_depart: int = ligne
    contenu: str = ""
    index_depart: int = index

    # garde-fou : 0 < index < len, sinon code_source[index] peut exploser ou boucler
    while (0 < index < len(code_source)
           and code_source[index] != "\n"
           and ligne_depart != 1):
        index -= 1

    if ligne != 1:
        for i in range(index_depart - index):
            contenu += code_source[index + i]
    else:
        message = f"À la première ligne // On first line : {message}"

    erreur(message, ligne_depart, contenu)

#---------------------------------------------------------------------------------------------
def un_seul_caractere(ligne: int, index: int, code_source: str, token: list[Token]) -> tuple[int, int]:
    ligne_depart: int = ligne
    index += 1

    if not index_Error(code_source, index):
        aide_remonter(index, code_source, ligne,
                      "Fichier terminé brutalement, inspecte la dernière ligne // File ends abruptly, check the last line 🔍")

    if not index_Error(code_source, index + 1) or code_source[index + 1] != "'":
        aide_remonter(index, code_source, ligne,
                      "Entre deux apostrophes '' il faut exactement UN caractère // Between two quotes '' there must be exactly ONE character ✋")

    token_append("CARACTERE", code_source[index], ligne_depart, token)
    index += 2
    return ligne, index

#---------------------------------------------------------------------------------------------
def chaine_caractere(ligne: int, index: int, code_source: str, token: list[Token]) -> tuple[int, int]:
    ligne_depart: int = ligne

    if not index_Error(code_source, index):
        aide_remonter(index, code_source, ligne,
                      "Fichier terminé brutalement, inspecte la dernière ligne // File ends abruptly, check the last line 🔍")

    index += 1
    depart = index

    while (index_Error(code_source, index)
           and code_source[index] != '"'
           and code_source[index] != "\n"):
        index += 1

    if index_Error(code_source, index) and code_source[index] != '"':
        aide_remonter(index, code_source, ligne,
                      "Chaîne non fermée // Unclosed string 🧵")
    if not index_Error(code_source, index):
        aide_remonter(index, code_source, ligne,
                      "Fin de fichier anormale // Abnormal end of file ⛔")

    valeur: str = code_source[depart:index]
    index += 1

    token_append("CHAINE_CARACTERE", valeur, ligne_depart, token)
    return ligne, index

#---------------------------------------------------------------------------------------------
def parenthese(ligne: int, index: int, code_source: str, token: list[Token]) -> tuple[int, int]:
    type_: str = "PAREN_OUVRANT" if code_source[index] == "(" else "PAREN_FERMANT"
    token_append(type_, code_source[index], ligne, token)
    index += 1
    return ligne, index

#---------------------------------------------------------------------------------------------
def numerique(ligne: int, index: int, code_source: str, token: list[Token]) -> tuple[int, int]:
    depart: int = index
    point_utiliser: bool = False

    while (index_Error(code_source, index)
           and (code_source[index].isdigit() or (code_source[index] == "." and not point_utiliser))
           and code_source[index] != "\n"):
        if code_source[index] == ".":
            point_utiliser = True
        index += 1

    if not code_source[index - 1].isdigit():
        aide_remonter(index, code_source, ligne,
                      "Les nombres doivent être des entiers ou réels sur une seule ligne // Numbers must be integers or reals on a single line 🔢")

    valeur = int(code_source[depart:index]) if not point_utiliser else float(code_source[depart:index])
    token_append("NOMBRE", valeur, ligne, token)
    return ligne, index

#---------------------------------------------------------------------------------------------
def symbole(ligne: int, index: int, code_source: str, token: list[Token], fichier: Langage) -> tuple[int, int]:
    valeur_un: str = code_source[index]
    index += 1

    if index_Error(code_source, index):
        valeur_deux: str = valeur_un + code_source[index]
        valide: bool
        type_: str
        valide, type_ = verificateur(valeur_deux, fichier)
        if valide:
            index += 1
            token_append(type_, valeur_deux, ligne, token)
            return ligne, index

    # fallback 1 caractère
    valide, type_ = verificateur(valeur_un, fichier)
    if not valide:
        aide_remonter(index, code_source, ligne,
                      f"Symbole non reconnu : '{valeur_un}' // Unrecognized symbol: '{valeur_un}' ❓")
    token_append(type_, valeur_un, ligne, token)
    return ligne, index

#---------------------------------------------------------------------------------------------
def verificateur(valeur: str, le_json: Langage) -> tuple[bool, str]:
    valide: bool = True
    type_: str = "identifiant"
    if valeur in le_json["mots_cles"]:
        type_ = "mots_cles"
    elif valeur in le_json["operateurs_logiques"]:
        type_ = "operateurs_logiques"
    elif valeur in le_json["operateurs_comparaison"]:
        type_ = "operateurs_comparaison"
    elif valeur in le_json["operateurs_arihmetiques"]:
        type_ = "operateurs_arihmetiques"
    elif valeur in le_json["valeur_booleen"]:
        type_ = "valeur_booleen"
    elif valeur in le_json["operateurs_affectation"]:
        type_ = "operateurs_affectation"
    elif valeur in le_json["separateur"]:
        type_ = "separateur"
    elif valeur in le_json["declaration_type"]:
        type_ = "declaration_type"
    else:
        valide = False
    return valide, type_

#---------------------------------------------------------------------------------------------
def alpha(ligne: int, index: int, code_source: str, token: list[Token], fichier: Langage) -> tuple[int, int]:
    depart_index: int = index

    # ✅ table pré-calculée dans avant_lexer, plus besoin de la reconstruire
    table: dict[str, str] = fichier["table_mots"]

    meilleur_fin_i: int = index
    meilleur_type: str = "identifiant"
    meilleur_valeur: str = ""

    temp_i: int = index
    mots: list[str] = []

    while len(mots) < MAX:
        mot: str = ""
        while (index_Error(code_source, temp_i)
               and (code_source[temp_i].isalnum() or code_source[temp_i] == "_")):
            mot += code_source[temp_i]
            temp_i += 1

        if mot == "":
            break

        mots.append(mot)
        candidat_norm: str = sans_accents(" ".join(mots))

        if candidat_norm in table:
            meilleur_fin_i = temp_i
            meilleur_type = table[candidat_norm]
            meilleur_valeur = candidat_norm

        debut_esp: int = temp_i
        while (index_Error(code_source, temp_i)
               and code_source[temp_i] in (" ", "\t")):
            temp_i += 1

        if temp_i == debut_esp:
            break

    if meilleur_type == "identifiant":
        mot_brut: str = mots[0]
        valeur: str = sans_accents(mot_brut)
        meilleur_fin_i = depart_index + len(mot_brut)
    else:
        valeur = meilleur_valeur

    token_append(meilleur_type, valeur, ligne, token)
    return ligne, meilleur_fin_i
