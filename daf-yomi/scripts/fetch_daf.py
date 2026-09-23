#!/usr/bin/env python3
"""Rassemble tout le materiel source d'un daf.

  python3 scripts/fetch_daf.py --jour 2026-09-23
  python3 scripts/fetch_daf.py "Bekhorot 5"

Ecrit fiches/<slug>.source.json : arameen segmente, traduction anglaise
d'appui (Davidson), commentateurs recuperes par l'API links, glossaire et
variantes textuelles du Kollel Iyun Hadaf, difficultes (insights), et les
liens de source. Aucun contenu n'est genere ici : c'est de la collecte.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402
import sefaria  # noqa: E402
import daf_calendar as C  # noqa: E402
import dafyomi_coil as K  # noqa: E402

paths.ensure()
COIL_CACHE = os.path.join(paths.CACHE, "coil")

COMMENTATEURS = ("Rashi", "Tosafot")


def slugify(libelle: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", libelle).strip("_")


def depuis_libelle(libelle: str) -> dict:
    """Reconstruit l'info d'un daf a partir de son libelle, sans date."""
    idx = {t["titre"]: t for t in C.bavli()["traites"]}
    m = re.match(r"^(.*?)\s+(\d+)([ab])?$", libelle.strip())
    if not m:
        raise SystemExit(f"libelle non reconnu : {libelle!r}")
    titre, num, amud = m.group(1), int(m.group(2)), m.group(3)
    t = idx.get(titre)
    if not t:
        raise SystemExit(f"traite inconnu : {titre!r}")
    refs = ([f"{titre}.{num}{amud}"] if amud
            else [f"{titre}.{num}a", f"{titre}.{num}b"])
    return {"libelle": libelle, "traite": titre, "traite_fr": t["nom_fr"],
            "seder": t["seder"], "daf": num, "amud": amud, "refs": refs,
            "dernier_daf": t["dernier_daf"], "dafyomi": t.get("dafyomi"),
            "background": bool(t.get("background")), "ref_api": None}


def collecte(d: dict) -> dict:
    amudim = {}
    for ref in d["refs"]:
        cle = ref.split(".")[-1] if "." in ref else ref
        a = sefaria.amoud(ref)
        amudim[cle] = {
            "ref": ref,
            "erreur": a.get("error"),
            "he": a["he"],
            "en": a["en"],
            "n_segments": len(a["he"]),
            "n_car_he": sum(len(s) for s in a["he"]),
            "url": sefaria.url(ref),
        }

    # Commentateurs : par l'API links, pas par la reference directe.
    comm = {}
    for ref in d["refs"]:
        cle = ref.split(".")[-1] if "." in ref else ref
        try:
            c = sefaria.commentateurs(ref, COMMENTATEURS)
        except Exception as exc:
            c = {n: [] for n in COMMENTATEURS}
            comm.setdefault("_erreurs", []).append(f"{ref}: {exc}")
        comm[cle] = {n: c.get(n, []) for n in COMMENTATEURS}

    couverture = {}
    for n in COMMENTATEURS:
        items = [x for cle, v in comm.items() if cle != "_erreurs"
                 for x in v.get(n, [])]
        couverture[n] = {"n_dibbourim": len(items),
                         "n_car": sum(len(x["he"]) for x in items)}

    # Kollel Iyun Hadaf
    bg = ins = None
    if d.get("dafyomi") and d.get("background"):
        s, p = d["dafyomi"]["slug"], d["dafyomi"]["prefix"]
        bg = K.background(s, p, d["daf"], COIL_CACHE)
        ins = K.insights(s, p, d["daf"], COIL_CACHE)

    return {
        "libelle": d["libelle"],
        "traite": d["traite"],
        "traite_fr": d["traite_fr"],
        "seder": d["seder"],
        "daf": d["daf"],
        "dernier_daf": d["dernier_daf"],
        "amudim": amudim,
        "commentateurs": comm,
        "couverture": couverture,
        "background": bg,
        "insights": ins,
        "sources": {
            "sefaria": [v["url"] for v in amudim.values()],
            "background": bg["url"] if bg else None,
            "insights": ins["url"] if ins else None,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("libelle", nargs="?", help='ex. "Bekhorot 5"')
    ap.add_argument("--jour", help="date ISO ; le daf vient du calendrier Sefaria")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if a.jour:
        d = C.jour(a.jour)
        if not d:
            raise SystemExit(f"aucun daf au {a.jour}")
    elif a.libelle:
        d = depuis_libelle(a.libelle)
    else:
        raise SystemExit("donner un libelle ou --jour AAAA-MM-JJ")

    doc = collecte(d)
    out = os.path.join(paths.FICHES, slugify(doc["libelle"]) + ".source.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)

    if not a.quiet:
        print(f"{doc['libelle']}  —  {doc['traite_fr']} {doc['daf']}"
              f"/{doc['dernier_daf']}, seder {doc['seder']}")
        for cle, v in doc["amudim"].items():
            if v["erreur"]:
                print(f"  {cle:6s} ERREUR : {v['erreur']}")
            else:
                print(f"  {cle:6s} {v['n_segments']:3d} segments, "
                      f"{v['n_car_he']:6d} car. arameen")
        for n, c in doc["couverture"].items():
            print(f"  {n:8s} {c['n_dibbourim']:3d} dibbourim, {c['n_car']:6d} car."
                  + ("   (aucun sur ce daf)" if not c["n_dibbourim"] else ""))
        if doc["background"]:
            b = doc["background"]
            print(f"  background : {len(b['entrees'])} entrées, "
                  f"{len(b['girsa'])} variantes   [{b.get('lignes_daf')}]")
        else:
            print("  background : indisponible pour ce traité")
        if doc["insights"]:
            print(f"  insights   : {len(doc['insights']['items'])} difficultés")
            for it in doc["insights"]["items"]:
                print(f"     {it['n']}. {it['titre'][:62]}"
                      + ("  [tronqué]" if it.get("tronque") else ""))
        print(f"  -> {os.path.relpath(out, paths.HOME)}")


if __name__ == "__main__":
    main()
