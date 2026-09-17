#!/usr/bin/env python3
"""Calendrier du programme Michna Yomit : generation et interrogation.

  python3 scripts/calendar_build.py build          # (re)genere data/calendar.json
  python3 scripts/calendar_build.py today
  python3 scripts/calendar_build.py date 2026-09-17
  python3 scripts/calendar_build.py progress
  python3 scripts/calendar_build.py find "Mishnah Oktzin 3:12"
  python3 scripts/calendar_build.py calibrate 2026-09-17 "Mishnah Oholot 2:4"
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

paths.ensure()
DATA = paths.DATA
TRACTATES = paths.data("tractates.json")
PROGRAM = paths.data("program.json")
CALENDAR = os.path.join(DATA, "calendar.json")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def flat_mishnayot(tractates):
    """Liste ordonnee de toutes les michnaiot du Shas : (ref, titre, ch, mich)."""
    out = []
    for t in tractates:
        for ci, count in enumerate(t["chapters"], start=1):
            for mi in range(1, count + 1):
                out.append({
                    "ref": f"{t['title']} {ci}:{mi}",
                    "tractate": t["title"],
                    "tractate_fr": t["name_fr"],
                    "seder": t["seder"],
                    "seder_fr": t["seder_fr"],
                    "chapter": ci,
                    "mishnah": mi,
                })
    return out


def rotate_to(seq, start_ref):
    for i, m in enumerate(seq):
        if m["ref"] == start_ref:
            return seq[i:] + seq[:i]
    raise SystemExit(f"start_ref introuvable : {start_ref}")


def study_dates(start: dt.date, n_days: int, skip: str):
    """Genere n_days dates d'etude en appliquant la regle de saut."""
    dates = []
    cur = start
    while len(dates) < n_days:
        wd = cur.weekday()  # lundi=0 ... samedi=5, dimanche=6
        if skip == "none" or not (skip.startswith("shabbat") and wd == 5):
            dates.append(cur)
        cur += dt.timedelta(days=1)
    return dates


def build():
    idx = load(TRACTATES)
    prog = load(PROGRAM)
    seq = rotate_to(flat_mishnayot(idx["tractates"]), prog["start_ref"])
    per_day = prog["per_day"]
    # Les editions ne decoupent pas les michnaiot identiquement. `offset` est
    # l'index, dans seq, de la premiere michna du premier jour : il recale tout
    # le calendrier sur une observation reelle (cf. bloc "calibration").
    offset = int(prog.get("offset_mishnayot", 0) or 0)
    n_days = -(-(len(seq) - offset) // per_day)
    dates = study_dates(dt.date.fromisoformat(prog["start_date"]), n_days,
                        prog.get("skip", "none"))

    days = []
    for i, d in enumerate(dates):
        base = i * per_day + offset
        chunk = [seq[j] for j in range(base, base + per_day) if 0 <= j < len(seq)]
        if not chunk:
            continue
        days.append({
            "day": len(days) + 1,
            "date": d.isoformat(),
            "weekday": d.strftime("%A"),
            "refs": [m["ref"] for m in chunk],
            "label": label_for(chunk),
            "tractates": list(dict.fromkeys(m["tractate"] for m in chunk)),
            "seder": chunk[0]["seder"],
            "first_index": base + 1,
        })

    payload = {
        "program": prog,
        "n_mishnayot": len(seq),
        "n_days": len(days),
        "start_date": days[0]["date"],
        "end_date": days[-1]["date"],
        "days": days,
    }
    with open(CALENDAR, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"{len(days)} jours, {len(seq)} michnaiot")
    print(f"debut {payload['start_date']} -> fin {payload['end_date']}")
    cal = prog.get("calibration")
    if cal:
        d = get_day(payload, cal["date"])
        got = d["refs"][0] if d else None
        ok = got == cal["expected_first_ref"]
        print(f"calibration {cal['date']} : attendu {cal['expected_first_ref']}, "
              f"obtenu {got} -> {'OK' if ok else 'ECART'}")
        if not ok:
            print("  ATTENTION : lancer `calibrate` pour recaler offset_mishnayot.")
    print(f"-> {CALENDAR}")


def label_for(chunk):
    """'Zeva'him 1:1-2' ou 'Ohalot 1:8 - 2:1' ou inter-traites."""
    a, b = chunk[0], chunk[-1]
    if a is b:
        return f"{a['tractate_fr']} {a['chapter']}:{a['mishnah']}"
    if a["tractate"] != b["tractate"]:
        return (f"{a['tractate_fr']} {a['chapter']}:{a['mishnah']} - "
                f"{b['tractate_fr']} {b['chapter']}:{b['mishnah']}")
    if a["chapter"] != b["chapter"]:
        return (f"{a['tractate_fr']} {a['chapter']}:{a['mishnah']} - "
                f"{b['chapter']}:{b['mishnah']}")
    return f"{a['tractate_fr']} {a['chapter']}:{a['mishnah']}-{b['mishnah']}"


def get_day(cal, date_iso):
    for d in cal["days"]:
        if d["date"] == date_iso:
            return d
    return None


def show(d, cal):
    if not d:
        print("Aucun jour de programme a cette date "
              f"(programme du {cal['start_date']} au {cal['end_date']}).")
        return
    print(f"Jour {d['day']}/{cal['n_days']}  -  {d['date']} ({d['weekday']})")
    print(f"  {d['label']}")
    for r in d["refs"]:
        print(f"    - {r}")


def progress(cal, today):
    done = [d for d in cal["days"] if d["date"] < today]
    n_done = sum(len(d["refs"]) for d in done)
    total = cal["n_mishnayot"]
    pct = 100.0 * n_done / total
    print(f"Programme : {cal['program']['name']}")
    print(f"Debut     : {cal['start_date']}  ({cal['days'][0]['label']})")
    print(f"Fin prevue: {cal['end_date']}  ({cal['days'][-1]['label']})")
    print()
    print(f"Michnaiot terminees : {n_done} / {total}  ({pct:.1f} %)")
    print(f"Jours ecoules       : {len(done)} / {cal['n_days']}")
    print(f"Restant             : {total - n_done} michnaiot, "
          f"{cal['n_days'] - len(done)} jours")
    print()
    cur = get_day(cal, today)
    if cur:
        print(f"Aujourd'hui ({today}) : {cur['label']}  [jour {cur['day']}]")
    # avancement par seder
    idx = load(TRACTATES)
    per_tr = {}
    for d in cal["days"]:
        for r in d["refs"]:
            tr = r.rsplit(" ", 1)[0]
            per_tr.setdefault(tr, {"done": 0, "total": 0})
            per_tr[tr]["total"] += 1
            if d["date"] < today:
                per_tr[tr]["done"] += 1
    print("\nAvancement par traite (ordre du cycle) :")
    seen = []
    for d in cal["days"]:
        for tr in d["tractates"]:
            if tr not in seen:
                seen.append(tr)
    byt = {t["title"]: t for t in idx["tractates"]}
    for tr in seen:
        s = per_tr[tr]
        mark = "OK " if s["done"] >= s["total"] else (">> " if s["done"] else "   ")
        print(f"  {mark}{byt[tr]['name_fr']:16s} {s['done']:4d}/{s['total']:<4d}")


def calibrate(date_iso: str, first_ref: str) -> None:
    """Calcule l'offset qui fait tomber `first_ref` le `date_iso`, l'ecrit
    dans program.json et regenere le calendrier."""
    prog = load(PROGRAM)
    idx = load(TRACTATES)
    seq = rotate_to(flat_mishnayot(idx["tractates"]), prog["start_ref"])
    per_day = prog["per_day"]
    n_days = -(-len(seq) // per_day)
    dates = study_dates(dt.date.fromisoformat(prog["start_date"]), n_days,
                        prog.get("skip", "none"))
    try:
        day_i = dates.index(dt.date.fromisoformat(date_iso))
    except ValueError:
        raise SystemExit(f"{date_iso} n'est pas un jour d'etude du programme")
    try:
        pos = next(i for i, m in enumerate(seq) if m["ref"] == first_ref)
    except StopIteration:
        raise SystemExit(f"reference inconnue : {first_ref}")
    offset = pos - day_i * per_day
    prog["offset_mishnayot"] = offset
    prog.setdefault("calibration", {})
    prog["calibration"].update({"date": date_iso, "expected_first_ref": first_ref})
    with open(PROGRAM, "w", encoding="utf-8") as fh:
        json.dump(prog, fh, ensure_ascii=False, indent=2)
    print(f"offset_mishnayot = {offset}  (ecrit dans data/program.json)")
    build()


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "today"
    if cmd == "build":
        return build()
    if cmd == "calibrate":
        return calibrate(sys.argv[2], sys.argv[3])
    cal = load(CALENDAR)
    today = os.environ.get("MICHNA_TODAY") or dt.date.today().isoformat()
    if cmd == "today":
        show(get_day(cal, today), cal)
    elif cmd == "date":
        show(get_day(cal, sys.argv[2]), cal)
    elif cmd == "progress":
        progress(cal, today)
    elif cmd == "find":
        target = sys.argv[2]
        for d in cal["days"]:
            if target in d["refs"]:
                return show(d, cal)
        print(f"{target} introuvable dans le calendrier.")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
