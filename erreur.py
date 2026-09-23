import sys

ROUGE = "\033[1m\033[91m"
VERT = "\033[1m\033[92m"
RESET = "\033[0m"
JAUNE = "\033[1m\033[93m"


def arret() -> None:
    sys.exit(1)


def gestion(message: str, ligne: int = -1, contenu: str = "", warning: bool = False) -> None:
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
