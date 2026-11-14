from dataclasses import dataclass, field
from TYPES_CREER.__lexer import Token, Langage, MAX
from UTILS.erreur import aide_remonter
from LEXER.aide_lexer import AideLexer
from UTILS.utils import sans_accents

@dataclass
class Lexer(AideLexer):
    le_json: Langage
    code_source: str
    _commentaire: list[str]

    token: list[Token] = field(default_factory=list())
    ligne: int = 1
    index: int = 0
    cas_symbole: list[str] = ["=", "<", ">", "+", "-", "*", "/", "^", "←", ":", ","]

    def __post_init__(self):
        self.orchestreur()

    def erreur(self, message: str = "", ligne_depart: int = -1) -> None:
        ligne_depart = self.ligne if ligne_depart != -1 else ligne_depart
        aide_remonter(
            self.index,
            self.code_source,
            ligne_depart,
            f"LEXER --> {message}",
        )

    def token_append(
        self,
        type_: str,
        valeur: str | int | float | None,
        ligne_depart: int = -1
    ) -> None:
        ligne_depart = self.ligne if ligne_depart != -1 else ligne_depart
        self.token.append({
            "type" : type_,
            "valeur" : valeur,
            "ligne" : ligne_depart,
        })

    def orchestreur(self) -> None:
        while self.index < len(self.code_source):
            caractere: str = self.code_source[self.index]

            if caractere in (" ", "\t"):
                self.espace()

            elif caractere == "\n":
                self.retour_ligne()

            elif caractere in _commentaire:
                self.commentaire()

            elif caractere == "'":
                self.un_seul_caractere()

            elif caractere == '"':
                self.chaine_caractere()

            elif caractere in ("(", ")"):
                self.parenthese()

            elif caractere.isdigit():
                self.numerique()

            elif caractere in cas_symbole:
                self.symbole()

            elif caractere.isalpha() or caractere == "_":
                self.alpha()

            else:
                self.erreur(
                    f"Terme non pris en charge : '{caractere}' // Unsupported token: '{caractere}' 🚫",
                )

        self.token_append("FIN_FICHIER", None, ligne, token)
