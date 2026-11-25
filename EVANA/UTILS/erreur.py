import sys

ROUGE = "\033[1m\033[91m"
VERT = "\033[1m\033[92m"
RESET = "\033[0m"
JAUNE = "\033[1m\033[93m"


def arret() -> None:
    sys.exit(1)

def aide_remonter(index: int, code_source: str, ligne: int, message: str) -> None:
    ligne_depart: int = ligne
    contenu: str = ""
    index_depart: int = index

    fin_ligne: int = index_depart
    while(
        fin_ligne < len(code_source)
        and code_source[fin_ligne] != "\n"
    ) :
        fin_ligne += 1

    if ligne != 1:
        contenu = f"[ici] {code_source[index_depart : fin_ligne]}"
    else:
        message = f"À la première ligne // On first line : {message}"

    erreur(message, ligne_depart, contenu)

def erreur(message: str, ligne: int = -1, contenu: str = "", warning: bool = False) -> None:
    if not warning:
        print(f"{ROUGE}Erreur grave 💥{RESET}")
        if contenu:
            print(f"  {ROUGE}{contenu}{RESET}")
        if ligne != -1:
            print(f"À la ligne {ligne} // At line {ligne}")
        print(f"GUIDE : {VERT}{message}{RESET}")
        arret()
    else:
        print(f"Interpellation {JAUNE}⚠️  : {message}{RESET}")
        if contenu:
            print(f"{contenu}")
