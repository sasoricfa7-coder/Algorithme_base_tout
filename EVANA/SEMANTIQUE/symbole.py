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
