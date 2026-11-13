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

from dataclasses import dataclass, field

@dataclass
class Symbole:
    nom: str
    type: str
    est_constante: bool = False
    parametres: list[str] = field(default_factory=list)
    nature: str = "variable"
    nb_dimensions: int = 0
    # --- NOUVEAUTÉS ---
    est_initialise: bool = False
    est_utilise: bool = False
    est_verrouille: bool = False
    est_lu: bool = False
    est_consomme: bool = False
    dimensions_statiques: list[int] = field(default_factory=list)
    ligne: int = -1
