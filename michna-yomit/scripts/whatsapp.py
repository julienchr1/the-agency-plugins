#!/usr/bin/env python3
"""Compose le message WhatsApp quotidien depuis les fiches du jour.

  python3 scripts/whatsapp.py --day 2026-09-17
  python3 scripts/whatsapp.py --day 2026-09-17 --lien "https://…" --copier

Format retenu : compact, mais avec pour chaque michna le texte hebreu, la
traduction francaise complete, les points essentiels, puis le lien vers les
fiches. N'envoie rien : produit le texte, a valider avant envoi.
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

paths.ensure()
ROOT = paths.HOME
FICHES = paths.FICHES
DATA = paths.DATA
SEP = "━━━━━━━━━━━━━━━"
NUM = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣"}

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = {0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi", 4: "vendredi",
         5: "samedi", 6: "dimanche"}


def slugify(ref: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", ref).strip("_")


def date_fr(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month - 1]} {d.year}"


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def jalons(cal: dict, day: dict) -> list[str]:
    """Detecte debut / fin de traite autour du jour courant."""
    out = []
    days = cal["days"]
    i = day["day"] - 1
    cur = day["tractates"]
    prev = days[i - 1]["tractates"] if i > 0 else []
    if len(cur) > 1:
        out.append(f"on termine {cur[0]} et on ouvre {cur[-1]} aujourd'hui")
    else:
        t = cur[0]
        if prev and t not in prev:
            out.append(f"premier jour de {t}")
        # combien de jours restent dans ce traite
        n = 0
        for d in days[i:]:
            if t in d["tractates"]:
                n += 1
            else:
                break
        if n <= 3:
            out.append(f"fin de {t} dans {n} jour{'s' if n > 1 else ''}")
    return out


def compose(day_iso: str, lien: str | None) -> str:
    cal = load(os.path.join(DATA, "calendar.json"))
    day = next((d for d in cal["days"] if d["date"] == day_iso), None)
    if not day:
        raise SystemExit(f"aucun jour de programme au {day_iso}")

    idx = load(os.path.join(DATA, "tractates.json"))
    byt = {t["title"]: t for t in idx["tractates"]}
    done = day["first_index"] - 1
    pct = 100.0 * done / cal["n_mishnayot"]

    L = [f"📖 *Michna Yomit* — {date_fr(day_iso)}",
         f"🗓 Jour {day['day']}/{cal['n_days']} · *{day['label']}* · "
         f"{pct:.1f} %".replace(".", ",")]
    for j in jalons(cal, day):
        L.append(f"🎯 {j}")
    L.append("")

    for k, ref in enumerate(day["refs"], start=1):
        slug = slugify(ref)
        sp, fp = (os.path.join(FICHES, slug + ".source.json"),
                  os.path.join(FICHES, slug + ".fr.json"))
        if not (os.path.exists(sp) and os.path.exists(fp)):
            raise SystemExit(f"fiche absente pour {ref} — lancer fetch_mishna.py "
                             f"puis rediger le .fr.json (skill michna-fiche)")
        src, fr = load(sp), load(fp)
        t = byt[src["tractate"]]
        L.append(SEP)
        L.append(f"{NUM.get(k, str(k))} *{t['name_fr']} "
                 f"{ref.rsplit(' ', 1)[1]}*")
        L.append("")
        L.append(f"_{src['michna']['hebreu']}_")
        L.append("")
        L.append(fr["traduction"].replace("*", "_"))
        L.append("")
        for p in fr.get("points_essentiels", []):
            L.append(f"💡 {p}")
        L.append("")

    L.append(SEP)
    if lien:
        L.append(f"📄 Fiches complètes (PDF) : {lien}")
    else:
        L.append("📄 Fiches complètes en pièce jointe.")
    first = day["refs"][0].replace(" ", "_").replace(":", ".")
    L.append(f"🔗 Sefaria : https://www.sefaria.org/{first}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=os.environ.get("MICHNA_TODAY")
                    or dt.date.today().isoformat())
    ap.add_argument("--lien")
    ap.add_argument("--copier", action="store_true",
                    help="copie le message dans le presse-papiers (macOS)")
    ap.add_argument("--out", help="ecrit aussi le message dans ce fichier")
    a = ap.parse_args()

    msg = compose(a.day, a.lien)
    print(msg)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(msg)
    if a.copier:
        try:
            subprocess.run(["pbcopy"], input=msg.encode("utf-8"), check=True)
            print("\n[message copie dans le presse-papiers]", file=sys.stderr)
        except Exception as exc:
            print(f"\n[copie impossible : {exc}]", file=sys.stderr)
    print(f"\n[{len(msg)} caracteres]", file=sys.stderr)


if __name__ == "__main__":
    main()
