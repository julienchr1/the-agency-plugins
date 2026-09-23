#!/usr/bin/env python3
"""Position dans le cycle Daf Yomi. La source est l'API calendrier de Sefaria :
aucun calcul de calendrier, donc aucune calibration possible.

  python3 scripts/daf_calendar.py today
  python3 scripts/daf_calendar.py date 2026-09-23
  python3 scripts/daf_calendar.py progress
  python3 scripts/daf_calendar.py jalons 2026-09-23
  python3 scripts/daf_calendar.py siyoum           # (re)cherche la fin de cycle
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402
import sefaria  # noqa: E402

paths.ensure()


def bavli() -> dict:
    with open(paths.data("bavli.json"), encoding="utf-8") as fh:
        return json.load(fh)


def aujourdhui() -> str:
    return os.environ.get("DAF_TODAY") or dt.date.today().isoformat()


def jour(date_iso: str) -> dict | None:
    """Le daf d'une date : libelle, traite, numero, references d'amudim."""
    e = sefaria.entree_calendrier(date_iso)
    if not e or not e.get("libelle"):
        return None
    val, ref_api = e["libelle"], e.get("ref")
    idx = {t["titre"]: t for t in bavli()["traites"]}
    # "Bekhorot 5", "Niddah 73a", "Shekalim 11"
    m = re.match(r"^(.*?)\s+(\d+)([ab])?$", val.strip())
    if not m:
        return {"date": date_iso, "libelle": val, "traite": None}
    titre, num, amud = m.group(1), int(m.group(2)), m.group(3)
    t = idx.get(titre)
    if t and t.get("yerushalmi"):
        # Chekalim : la plage fournie par l'API fait foi, pas le libelle.
        refs = [ref_api or val]
    elif amud:
        refs = [f"{titre}.{num}{amud}"]
    else:
        refs = [f"{titre}.{num}a", f"{titre}.{num}b"]
    return {
        "date": date_iso,
        "libelle": val,
        "ref_api": ref_api,
        "traite": titre,
        "traite_fr": t["nom_fr"] if t else titre,
        "seder": t["seder"] if t else None,
        "daf": num,
        "amud": amud,
        "refs": refs,
        "dernier_daf": t["dernier_daf"] if t else None,
        "dafyomi": t.get("dafyomi") if t else None,
        "background": bool(t and t.get("background")),
    }


def siyoum(force: bool = False) -> dict:
    """Trouve la derniere date du cycle en cours, par recherche bornee."""
    p = paths.data("cycle.json")
    if os.path.exists(p) and not force:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    d0 = dt.date.fromisoformat(aujourdhui())
    lo, hi = d0, d0 + dt.timedelta(days=3 * 365)
    if sefaria.daf_du_jour(hi.isoformat()):
        info = {"fin": None, "note": "fin de cycle au-dela de trois ans"}
    else:
        while (hi - lo).days > 1:
            mid = lo + (hi - lo) / 2
            if sefaria.daf_du_jour(mid.isoformat()):
                lo = mid
            else:
                hi = mid
        info = {"fin": lo.isoformat(), "dernier": sefaria.daf_du_jour(lo.isoformat())}
    info["verifie_le"] = aujourdhui()
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(info, fh, ensure_ascii=False, indent=2)
    return info


def jalons(date_iso: str) -> list[dict]:
    """Debut / fin de traite, changement de seder, autour d'une date."""
    d = jour(date_iso)
    if not d or not d.get("traite"):
        return []
    base = dt.date.fromisoformat(date_iso)
    veille = jour((base - dt.timedelta(days=1)).isoformat())
    lend = jour((base + dt.timedelta(days=1)).isoformat())
    ev = []
    if not veille or veille.get("traite") != d["traite"]:
        ev.append({"type": "debut_massekhet", "traite": d["traite"],
                   "traite_fr": d["traite_fr"], "seder": d["seder"],
                   "dernier_daf": d["dernier_daf"]})
    if not lend or lend.get("traite") != d["traite"]:
        ev.append({"type": "fin_massekhet", "traite": d["traite"],
                   "traite_fr": d["traite_fr"], "seder": d["seder"],
                   "suivant": lend["traite_fr"] if lend else None})
    if veille and lend and veille.get("seder") != d.get("seder"):
        ev.append({"type": "debut_seder", "seder": d["seder"]})
    if lend and lend.get("seder") and lend["seder"] != d.get("seder"):
        ev.append({"type": "fin_seder", "seder": d["seder"]})
    return ev


# ------------------------------------------------------------------ affichage
def montre(d, date_iso):
    if not d:
        print(f"Aucun daf au {date_iso} (hors cycle connu de Sefaria).")
        return
    j = dt.date.fromisoformat(date_iso)
    print(f"{date_iso} ({j.strftime('%A')}) — {d['libelle']}")
    if d.get("traite"):
        print(f"  {d['traite_fr']} {d['daf']}{d['amud'] or ''} "
              f"sur {d['dernier_daf']} — seder {d['seder']}")
        print(f"  references : {', '.join(d['refs'])}")
        if not d["background"]:
            print("  (pas de pages background sur dafyomi.co.il pour ce traite)")


def progress():
    t = aujourdhui()
    d = jour(t)
    montre(d, t)
    c = siyoum()
    if c.get("fin"):
        reste = (dt.date.fromisoformat(c["fin"]) - dt.date.fromisoformat(t)).days
        print(f"\nSiyoum haShas : {c['fin']} ({c.get('dernier')}) — "
              f"dans {reste} jours")
    if d and d.get("traite"):
        fait = d["daf"] - 1
        total = d["dernier_daf"] - 1
        reste_t = total - fait
        print(f"\n{d['traite_fr']} : {fait} dafim faits sur {total}, "
              f"{reste_t} restants (~{reste_t} jours)")
        for e in jalons(t):
            print(f"  JALON {e['type']}"
                  + (f" — suivant : {e['suivant']}" if e.get("suivant") else ""))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "today"
    if cmd == "today":
        t = aujourdhui()
        montre(jour(t), t)
    elif cmd == "date":
        montre(jour(sys.argv[2]), sys.argv[2])
    elif cmd == "progress":
        progress()
    elif cmd == "jalons":
        d = sys.argv[2] if len(sys.argv) > 2 else aujourdhui()
        ev = jalons(d)
        print(json.dumps({"date": d, "jalons": ev}, ensure_ascii=False, indent=2)
              if ev else f"{d} : aucun jalon")
    elif cmd == "siyoum":
        print(json.dumps(siyoum(force=True), ensure_ascii=False, indent=2))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
