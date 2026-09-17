#!/usr/bin/env python3
"""Evenements du cycle et controle de l'etat des fiches.

  python3 scripts/check.py events 2026-09-20     # jalons autour d'une date
  python3 scripts/check.py tractate "Mishnah Oholot"
  python3 scripts/check.py audit                 # fiches manquantes/incompletes
  python3 scripts/check.py audit --from 2026-09-01
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

paths.ensure()
ROOT = paths.HOME
DATA = paths.DATA
FICHES = paths.FICHES


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def slugify(ref: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", ref).strip("_")


def tractate_span(cal, title):
    """(premier jour, dernier jour, nb de jours) d'un traite dans le cycle."""
    ds = [d for d in cal["days"] if title in d["tractates"]]
    return (ds[0], ds[-1], len(ds)) if ds else (None, None, 0)


def cmd_events(date_iso):
    cal, idx = load("calendar.json"), load("tractates.json")
    byt = {t["title"]: t for t in idx["tractates"]}
    day = next((d for d in cal["days"] if d["date"] == date_iso), None)
    if not day:
        return print(f"aucun jour de programme au {date_iso}")
    i = day["day"] - 1
    prev = cal["days"][i - 1] if i > 0 else None
    nxt = cal["days"][i + 1] if i + 1 < len(cal["days"]) else None

    print(f"{date_iso} — jour {day['day']}/{cal['n_days']} — {day['label']}")
    events = []
    for title in day["tractates"]:
        t = byt[title]
        first, last, n = tractate_span(cal, title)
        if first["date"] == date_iso:
            events.append({
                "type": "debut_massekhet", "tractate": title,
                "nom_fr": t["name_fr"], "seder_fr": t["seder_fr"],
                "n_chapitres": t["n_chapters"], "n_michnaiot": t["n_mishnayot"],
                "n_jours": n, "fin_prevue": last["date"],
            })
        if last["date"] == date_iso:
            events.append({
                "type": "fin_massekhet", "tractate": title,
                "nom_fr": t["name_fr"], "seder_fr": t["seder_fr"],
                "n_chapitres": t["n_chapters"], "n_michnaiot": t["n_mishnayot"],
                "n_jours": n, "debut": first["date"],
            })
    if prev and prev["seder"] != day["seder"]:
        events.append({"type": "debut_seder", "seder": day["seder"]})
    if nxt and nxt["seder"] != day["seder"]:
        events.append({"type": "fin_seder", "seder": day["seder"]})

    if not events:
        # proximite d'un jalon : utile pour annoncer a l'avance
        title = day["tractates"][-1]
        first, last, n = tractate_span(cal, title)
        reste = sum(1 for d in cal["days"][i:] if title in d["tractates"])
        print(f"  aucun jalon. {byt[title]['name_fr']} : {reste} jour(s) "
              f"restant(s), fin le {last['date']}")
    for e in events:
        print(f"  JALON {e['type']}")
        for k, v in e.items():
            if k != "type":
                print(f"    {k}: {v}")
    print()
    print(json.dumps({"date": date_iso, "day": day["day"], "refs": day["refs"],
                      "label": day["label"], "events": events},
                     ensure_ascii=False, indent=2))


def cmd_tractate(title):
    cal, idx = load("calendar.json"), load("tractates.json")
    byt = {t["title"]: t for t in idx["tractates"]}
    if title not in byt:
        cands = [k for k in byt if title.lower() in k.lower()
                 or title.lower() in byt[k]["name_fr"].lower()]
        if len(cands) != 1:
            return print(f"traite ambigu ou inconnu : {title!r}\n  {cands[:8]}")
        title = cands[0]
    t = byt[title]
    first, last, n = tractate_span(cal, title)
    print(f"{t['name_fr']} ({title}) — {t['he_title']}")
    print(f"  seder        : {t['seder_fr']}")
    print(f"  chapitres    : {t['n_chapters']}  ({', '.join(map(str, t['chapters']))})")
    print(f"  michnaiot    : {t['n_mishnayot']}")
    print(f"  bartenura    : {t['bartenura_title'] or 'ABSENT'}")
    if first:
        print(f"  dans le cycle: {first['date']} -> {last['date']}  ({n} jours)")


def cmd_audit(date_from, date_to):
    cal = load("calendar.json")
    today = os.environ.get("MICHNA_TODAY") or dt.date.today().isoformat()
    date_to = date_to or today
    days = [d for d in cal["days"]
            if (not date_from or d["date"] >= date_from) and d["date"] <= date_to]
    if not days:
        return print("aucun jour dans l'intervalle")

    manquantes, incompletes, ok = [], [], 0
    for d in days:
        for ref in d["refs"]:
            s = slugify(ref)
            src = os.path.join(FICHES, s + ".source.json")
            fr = os.path.join(FICHES, s + ".fr.json")
            md = os.path.join(FICHES, s + ".md")
            pdf = os.path.join(FICHES, s + ".pdf")
            if not os.path.exists(fr):
                manquantes.append((d["date"], ref))
                continue
            pbs = []
            if not os.path.exists(md):
                pbs.append("md absent")
            if not os.path.exists(pdf):
                pbs.append("pdf absent")
            if os.path.exists(src):
                with open(src, encoding="utf-8") as fh:
                    n = json.load(fh)["bartenura"]["n_sections"]
                with open(fr, encoding="utf-8") as fh:
                    got = {int(b["n"]) for b in json.load(fh).get("bartenura", [])
                           if b.get("traduction", "").strip()}
                miss = [i for i in range(1, n + 1) if i not in got]
                if miss:
                    pbs.append(f"bartenura: sections manquantes {miss} (sur {n})")
            if pbs:
                incompletes.append((d["date"], ref, pbs))
            else:
                ok += 1

    tot = sum(len(d["refs"]) for d in days)
    print(f"Periode {days[0]['date']} -> {days[-1]['date']}  "
          f"({len(days)} jours, {tot} michnaiot)")
    print(f"  completes   : {ok}")
    print(f"  incompletes : {len(incompletes)}")
    print(f"  absentes    : {len(manquantes)}")
    if manquantes:
        print("\nFiches absentes :")
        for dte, ref in manquantes:
            print(f"  {dte}  {ref}")
    if incompletes:
        print("\nFiches incompletes :")
        for dte, ref, pbs in incompletes:
            print(f"  {dte}  {ref} — {'; '.join(pbs)}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("events"); p.add_argument("date")
    p = sub.add_parser("tractate"); p.add_argument("title")
    p = sub.add_parser("audit")
    p.add_argument("--from", dest="date_from")
    p.add_argument("--to", dest="date_to")
    a = ap.parse_args()
    if a.cmd == "events":
        cmd_events(a.date)
    elif a.cmd == "tractate":
        cmd_tractate(a.title)
    else:
        cmd_audit(a.date_from, a.date_to)


if __name__ == "__main__":
    main()
