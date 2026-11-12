from dataclasses import dataclass, field
from SEMANTIQUE.symbole import Symbole

@dataclass
class TableSymboles:
    pile: list[dict[str, Symbole]] = field(default_factory=list)
    noms_globaux: set[str] = field(default_factory=set)

    def entrer_portee(self) -> None:
        self.pile.append({})

    def sortir_portee(self) -> None:
        portee_actuelle: dict = self.pile[-1]

        for nom, symbole in portee_actuelle.items():
            if symbole.nature == "variable" and symbole.est_lu and not symbole.est_consomme:
                self.erreur(f"La variable '{nom}' est lue mais sa valeur n'est jamais exploitée 🚫", symbole.ligne)
        
            if not symbole.est_utilise and symbole.nature in ("variable", "constante", "tableau", "fonction", "procedure"):

                match symbole.nature:
                    case "variable": vrai_nom = "La variable"
                    case "constante": vrai_nom = "La constante"
                    case "tableau": vrai_nom = "Le tableau"
                    case "fonction": vrai_nom = "La fonction"
                    case "procedure": vrai_nom = "La procedure"
                    case _ : vrai_nom = symbole
                self.erreur(f"{vrai_nom}  '{nom}' est déclaré mais jamais utilisé 🚫", symbole.ligne)
        self.pile.pop()

    def declarer(self, nom: str, symbole: Symbole) -> None:
        if nom == "racine":
            self.erreur("Le nom 'racine' est réservé par le langage pour la fonction racine carrée 🚫", symbole.ligne)
        if nom == "sqrt":
            self.erreur("Le nom 'sqrt' est réservé par le langage pour la fonction racine carrée 🚫", symbole.ligne)
        if nom in self.pile[-1]:
            self.erreur(f"Le symbole '{nom}' est déjà déclaré dans cette portée 🚫", symbole.ligne)

        if symbole.nature in ("fonction", "procedure") or len(self.pile) == 1:
            if nom in self.noms_globaux:
                self.erreur(f"Le symbole global '{nom}' est déjà déclaré 🚫 : NB: aucune donnée ne doit avoir le nom de votre algorithme.", symbole.ligne)
            self.noms_globaux.add(nom)

        self.pile[-1][nom] = symbole

    def rechercher(self, nom: str, ligne: int = -1) -> Symbole:
        for portee in reversed(self.pile):
            if nom in portee:
                return portee[nom]
        self.erreur(f"Le symbole '{nom}' n'est pas déclaré 🚫", ligne) 
        #%Car dans un gros programme on veut savoir exactement ou on a pas declaré%

    def erreur(self, message: str ="", ligne: int = -1) -> None:
        message = f"Analyseur_semantique → {message}"
        erreur(message, ligne)
