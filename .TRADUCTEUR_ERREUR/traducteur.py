#!/usr/bin/env python3
"""
Traducteur Anglais -> Français, 100% hors ligne après installation.

Moteur : Argos Translate (traduction neuronale via CTranslate2).
Pas de dictionnaire mot-à-mot : le modèle traduit des phrases entières
en tenant compte du contexte, comme un vrai traducteur automatique.

Léger en RAM (adapté à une machine à 4 Go), contrairement aux pipelines
transformers/PyTorch classiques.

Usage :
    python traducteur.py fichier.txt
"""

import os

# IMPORTANT : doit être fait AVANT d'importer argostranslate.
# Force l'utilisation de MiniSBD (léger, ONNX) au lieu de Stanza
# (PyTorch) pour découper les phrases. Stanza tente sinon de
# recontacter raw.githubusercontent.com à CHAQUE traduction, même
# hors ligne après installation du modèle -- MiniSBD ne le fait
# qu'une fois, puis reste en cache local.
os.environ.setdefault("ARGOS_CHUNK_TYPE", "MINISBD")

import sys
from pathlib import Path

import argostranslate.package
import argostranslate.translate

CODE_SRC = "en"
CODE_DST = "fr"


def modele_deja_installe() -> bool:
    langues = argostranslate.translate.get_installed_languages()
    codes = [lang.code for lang in langues]
    return CODE_SRC in codes and CODE_DST in codes


def installer_modele() -> None:
    """Télécharge et installe le modèle EN->FR.
    A faire UNE SEULE FOIS, nécessite une connexion internet.
    Ensuite, tout fonctionne hors ligne, même sans réseau."""
    print("Mise à jour de l'index des paquets...", file=sys.stderr)
    argostranslate.package.update_package_index()
    paquets = argostranslate.package.get_available_packages()

    paquet_en_fr = next(
        (p for p in paquets if p.from_code == CODE_SRC and p.to_code == CODE_DST),
        None,
    )
    if paquet_en_fr is None:
        print("Erreur : impossible de trouver le paquet en->fr dans l'index.", file=sys.stderr)
        sys.exit(1)

    print("Téléchargement du modèle en->fr (quelques dizaines de Mo)...", file=sys.stderr)
    chemin = paquet_en_fr.download()
    argostranslate.package.install_from_path(chemin)
    print("Modèle installé. Il est maintenant disponible hors ligne.\n", file=sys.stderr)


def traduire(texte: str) -> str:
    langues = argostranslate.translate.get_installed_languages()
    langue_en = next(l for l in langues if l.code == CODE_SRC)
    langue_fr = next(l for l in langues if l.code == CODE_DST)
    traduction = langue_en.get_translation(langue_fr)
    return traduction.translate(texte)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage : python traducteur.py <fichier.txt>", file=sys.stderr)
        sys.exit(1)

    chemin_fichier = Path(sys.argv[1])
    if not chemin_fichier.is_file():
        print(f"Erreur : fichier introuvable -> {chemin_fichier}", file=sys.stderr)
        sys.exit(1)

    if not modele_deja_installe():
        installer_modele()

    texte = chemin_fichier.read_text(encoding="utf-8")
    resultat = traduire(texte)
    print(resultat)


if __name__ == "__main__":
    main()
