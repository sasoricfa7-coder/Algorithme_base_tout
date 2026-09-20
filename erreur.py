import sys

ROUGE = "\033[1m\033[91m"
VERT = "\033[1m\033[92m"
RESET = "\033[0m"
JAUNE = "\033[1m\033[93m"

def arret() :
    sys.exit(1)
def gestion(message: str, ligne: int = None, colonne: int = None, contenu: str = "", warning: bool = False) :
    if not warning :
        print(f"{ROUGE} Erreur grave {contenu} {RESET}")    
        if ligne is not None : 
            print("A la ligne {ligne}")
        if colonne is not None :
            print("A la colonne {colonne}")
        print(f"GUIDE : {VERT} {message} {RESET}")
        arret()

    else :
        print(f"Interpellation {JAUNE} : {message} {RESET}")
        print(f"{contenu}")
