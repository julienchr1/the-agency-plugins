#!/usr/bin/env python3
"""Audit du Daf Yomi : etat des fiches, jalons a venir, sante des sources.

  python3 scripts/check.py audit --from 2026-09-01
  python3 scripts/check.py jalons --jours 14
  python3 scripts/check.py sources
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402
import sefaria  # noqa: E402
import daf_calendar as C  # noqa: E402

paths.ensure()


def slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def etat(slug: str) -> tuple[str, list[str]]:
    f = lambda suf: os.path.join(paths.FICHES, slug + suf)  # noqa: E731
    if not os.path.exists(f(".source.json")):
        return "collecte absente", []
    if not os.path.exists(f(".fr.json")):
        return "francais absent", []
    manque = [n for n, suf in (("B .pdf", "_B.pdf"),
                               ("B-light .pdf", "_B-light.pdf"),
                               ("B .md", "_B.md"),
                               ("B-light .md", "_B-light.md"))
              if not os.path.exists(f(suf))]
    return ("complet" if not manque else "partiel"), manque


def cmd_audit(date_from: str | None, date_to: str | None):
    today = os.environ.get("DAF_TODAY") or dt.date.today().isoformat()
    fin = dt.date.fromisoformat(date_to or today)
    debut = dt.date.fromisoformat(date_from) if date_from else fin - dt.timedelta(days=13)
    par_etat: dict[str, list] = {}
    d = debut
    while d <= fin:
        j = C.jour(d.isoformat())
        if j:
            e, manque = etat(slugify(j["libelle"]))
            par_etat.setdefault(e, []).append((d.isoformat(), j["libelle"], manque))
        d += dt.timedelta(days=1)
    total = sum(len(v) for v in par_etat.values())
    print(f"Période {debut} → {fin}  ({total} dafim)")
    for e in ("complet", "partiel", "francais absent", "collecte absente"):
        if e in par_etat:
            print(f"  {e:18s} {len(par_etat[e])}")
    for e in ("partiel", "francais absent", "collecte absente"):
        for dte, lib, manque in par_etat.get(e, []):
            print(f"\n  {dte}  {lib}  — {e}"
                  + (f" : manque {', '.join(manque)}" if manque else ""))


def cmd_jalons(jours: int):
    """Jalons sur une plage, calcules depuis un seul ancrage puis recoupes
    avec l'API sur quelques points. Interroger l'API date par date faisait
    des dizaines de requetes et declenchait des reponses 429."""
    today = os.environ.get("DAF_TODAY") or dt.date.today().isoformat()
    seq = C.sequence(today, jours)
    if not seq:
        print(f"Aucun daf au {today}.")
        return
    trouve = False
    for i, j in enumerate(seq):
        veille = seq[i - 1] if i else None
        lend = seq[i + 1] if i + 1 < len(seq) else None
        if veille and veille["traite"] != j["traite"]:
            trouve = True
            print(f"  {j['date']}  debut_massekhet — {j['traite_fr']} "
                  f"({j['dernier_daf'] - 1} dafim)")
        if lend and lend["traite"] != j["traite"]:
            trouve = True
            print(f"  {j['date']}  fin_massekhet — {j['traite_fr']} "
                  f"→ {lend['traite_fr']}")
            if lend["seder"] != j["seder"]:
                print(f"  {j['date']}  fin_seder — {j['seder']} → {lend['seder']}")
    if not trouve:
        print(f"Aucun jalon dans les {jours} prochains jours.")
    v = C.verifie_sequence(seq)
    msg = f"\n  recoupement avec l'API : {v['etat']}"
    if v["verifies"]:
        msg += f" ({v['verifies']} point(s) vérifié(s))"
    if v["ecarts"]:
        msg += " — " + " ; ".join(v["ecarts"])
    print(msg)


def cmd_sources():
    today = os.environ.get("DAF_TODAY") or dt.date.today().isoformat()
    ok = True
    try:
        v = sefaria.daf_du_jour(today)
        print(f"  calendrier Sefaria : {v or 'AUCUN DAF'}")
        ok = ok and bool(v)
    except Exception as exc:
        print(f"  calendrier Sefaria : ERREUR {exc}")
        ok = False
    try:
        a = sefaria.amoud("Berakhot.2a")
        print(f"  texte Sefaria      : {len(a['he'])} segments sur Berakhot 2a")
        ok = ok and bool(a["he"])
    except Exception as exc:
        print(f"  texte Sefaria      : ERREUR {exc}")
        ok = False
    import urllib.request
    u = "https://www.dafyomi.co.il/bechoros/backgrnd/be-in-005.htm"
    try:
        with urllib.request.urlopen(
                urllib.request.Request(u, method="HEAD"), timeout=20) as r:
            print(f"  Kollel Iyun Hadaf  : HTTP {r.status}")
            ok = ok and r.status == 200
    except Exception as exc:
        print(f"  Kollel Iyun Hadaf  : ERREUR {exc}")
        ok = False
    cyc = C.siyoum()
    if cyc.get("fin"):
        reste = (dt.date.fromisoformat(cyc["fin"])
                 - dt.date.fromisoformat(today)).days
        print(f"  fin de cycle       : {cyc['fin']} ({cyc.get('dernier')}), "
              f"dans {reste} jours")
        if reste < 60:
            print("  ATTENTION : fin de cycle proche — prévoir le cycle suivant.")
    print("\n  ->", "tout répond" if ok else "au moins une source est en défaut")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("audit")
    p.add_argument("--from", dest="date_from")
    p.add_argument("--to", dest="date_to")
    p = sub.add_parser("jalons")
    p.add_argument("--jours", type=int, default=14)
    sub.add_parser("sources")
    a = ap.parse_args()
    if a.cmd == "audit":
        cmd_audit(a.date_from, a.date_to)
    elif a.cmd == "jalons":
        cmd_jalons(a.jours)
    else:
        cmd_sources()


if __name__ == "__main__":
    main()
