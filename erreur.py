import sys

ROUGE = "\033[1m\033[91m"
VERT = "\033[1m\033[92m"
RESET = "\033[0m"
JAUNE = "\033[1m\033[93m"

def arret() :
    sys.exit(1)
def gestion(message: str, ligne: int = -1, colonne: int = -1, contenu: str = "", warning: bool = False) :
    if not warning :
        print(f"{ROUGE} Erreur grave {contenu} {RESET}")    
        if ligne != -1 : 
            print(f"A la ligne {ligne}")
        if colonne != -1 :
            print(f"A la colonne {colonne}")
        print(f"GUIDE : {VERT} {message} {RESET}")
        arret()

    else :
        print(f"Interpellation {JAUNE} : {message} {RESET}")
        print(f"{contenu}")
