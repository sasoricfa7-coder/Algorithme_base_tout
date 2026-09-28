# utils.py
import unicodedata

def sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFD", texte)
    sans = "".join(c for c in decompose if unicodedata.category(c) != "Mn")
    return sans.strip().lower()
