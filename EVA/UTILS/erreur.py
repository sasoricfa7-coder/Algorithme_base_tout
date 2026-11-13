# EVA - Langage Algorithmique Pédagogique
# Copyright (C) 2026 SASORI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

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
