#!/usr/bin/env python3
"""Compose le message WhatsApp quotidien du Daf Yomi.

  python3 scripts/whatsapp.py --jour 2026-09-23 --out messages/2026-09-23.txt

N'envoie rien : produit le texte, a valider avant envoi. Contrairement a la
michna, le texte du daf n'est pas cite — il est trop long. Ce sont la structure
et les points saillants qui passent.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402
import daf_calendar as C  # noqa: E402

paths.ensure()
SEP = "━━━━━━━━━━━━━━━"
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = {0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi", 4: "vendredi",
         5: "samedi", 6: "dimanche"}

# Les fiches sont en Markdown (*terme* italique, **mot** gras) ; WhatsApp
# inverse (*gras*, _italique_). Conversion en deux passes avec une marque
# intermediaire, sinon le gras est casse.
MD_BOLD = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", re.S)
MD_ITAL = re.compile(r"(?<!\*)\*(?=\S)([^*]+?)(?<=\S)\*(?!\*)", re.S)
_MARK = "\x00"


def wa(s) -> str:
    out = MD_BOLD.sub(lambda m: _MARK + m.group(1) + _MARK, s or "")
    out = MD_ITAL.sub(r"_\1_", out)
    return out.replace(_MARK, "*")


def date_fr(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month - 1]} {d.year}"


def slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def compose(date_iso: str, lien: str | None, entete_extra: str | None) -> str:
    d = C.jour(date_iso)
    if not d:
        raise SystemExit(f"aucun daf au {date_iso}")
    slug = slugify(d["libelle"])
    fp = os.path.join(paths.FICHES, slug + ".fr.json")
    if not os.path.exists(fp):
        raise SystemExit(f"fiche absente pour {d['libelle']} — lancer "
                         f"fetch_daf.py puis rediger le .fr.json "
                         f"(skill daf-fiche)")
    with open(fp, encoding="utf-8") as fh:
        fr = json.load(fh)

    L = [f"📖 *Daf Yomi* — {date_fr(date_iso)}",
         f"📗 *{d['traite_fr']} {d['daf']}* · daf {d['daf'] - 1}"
         f"/{d['dernier_daf'] - 1} du traité · seder {d['seder']}"]
    cyc = C.siyoum()
    if cyc.get("fin"):
        reste = (dt.date.fromisoformat(cyc["fin"])
                 - dt.date.fromisoformat(date_iso)).days
        L.append(f"🏁 Siyoum haShas dans {reste} jours")
    for e in C.jalons(date_iso):
        if e["type"] == "debut_massekhet":
            L.append(f"🎯 Premier daf de {e['traite_fr']}")
        elif e["type"] == "fin_massekhet":
            L.append(f"🎉 Dernier daf de {e['traite_fr']}"
                     + (f" — demain, {e['suivant']}" if e.get("suivant") else ""))
    L.append("")
    if entete_extra:
        L += [entete_extra.strip(), ""]
    if fr.get("titre_court"):
        L += [wa(fr["titre_court"]), ""]

    L.append(SEP)
    for p in fr.get("points_whatsapp") or []:
        L.append(f"💡 {wa(p)}")
    L.append("")
    L.append(SEP)
    if lien:
        L.append(f"📄 Fiches complètes : {lien}")
    else:
        L.append("📄 Fiches complètes en pièce jointe (version longue et version courte).")
    L.append(f"🔗 Sefaria : https://www.sefaria.org/{d['refs'][0]}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jour", default=os.environ.get("DAF_TODAY")
                    or dt.date.today().isoformat())
    ap.add_argument("--lien")
    ap.add_argument("--entete", help="bloc a placer en tete (hadran, siyoum…)")
    ap.add_argument("--out")
    ap.add_argument("--copier", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    msg = compose(a.jour, a.lien, a.entete)
    print(msg)
    if a.out:
        p = a.out if os.path.isabs(a.out) else os.path.join(paths.HOME, a.out)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(msg if msg.endswith("\n") else msg + "\n")
    if a.copier:
        try:
            subprocess.run(["pbcopy"], input=msg.encode("utf-8"), check=True)
            if a.verbose:
                print("[copié dans le presse-papiers]", file=sys.stderr)
        except Exception as exc:
            print(f"[copie impossible : {exc}]", file=sys.stderr)
    if a.verbose:
        print(f"[{len(msg)} caractères]", file=sys.stderr)


if __name__ == "__main__":
    main()
