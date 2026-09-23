"""Emplacements de travail du plugin.

Le plugin installe est une copie en lecture seule dans le cache de Claude Code
(`~/.claude/plugins/cache/...`), effacee a chaque mise a jour. Les donnees qui
vivent — calendrier, calibration, fiches, cache Sefaria — ne doivent donc PAS
y etre ecrites.

Elles vont dans le dossier de travail, dans cet ordre de priorite :
  1. $DAF_HOME
  2. un fichier .daf-yomi dans le repertoire courant (vide = travailler
     ici ; sinon il contient le chemin du dossier de travail)
  3. le repertoire courant s'il contient deja data/program.json
  4. ~/Documents/Daf Yomi

Les donnees de reference livrees avec le plugin (les 63 traites, la table
dafyomi, le programme) sont recopiees dans le dossier de travail au premier
usage, puis c'est cette copie qui fait foi.
"""
from __future__ import annotations

import os
import shutil

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_DATA = os.path.join(PLUGIN_ROOT, "data")

SEED_FILES = ("bavli.json", "dafyomi_slugs.json")


MARKER = ".daf-yomi"


def _resolve_home() -> str:
    env = os.environ.get("DAF_HOME")
    if env:
        return os.path.abspath(os.path.expanduser(env))
    cwd = os.path.abspath(os.getcwd())
    marker = os.path.join(cwd, MARKER)
    if os.path.isfile(marker):
        try:
            with open(marker, encoding="utf-8") as fh:
                target = fh.read().strip()
        except OSError:
            target = ""
        if target:
            return os.path.abspath(os.path.expanduser(target))
        return cwd
    if os.path.exists(os.path.join(cwd, "data", "program.json")):
        return cwd
    return os.path.expanduser("~/Documents/Daf Yomi")


HOME = _resolve_home()
DATA = os.path.join(HOME, "data")
FICHES = os.path.join(HOME, "fiches")
CACHE = os.path.join(DATA, "cache")


def ensure() -> str:
    """Cree le dossier de travail et y recopie les donnees de reference
    manquantes. Idempotent."""
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(FICHES, exist_ok=True)
    if os.path.abspath(HOME) != os.path.abspath(PLUGIN_ROOT):
        for name in SEED_FILES:
            src = os.path.join(PLUGIN_DATA, name)
            dst = os.path.join(DATA, name)
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
    return HOME


def data(name: str) -> str:
    ensure()
    return os.path.join(DATA, name)
