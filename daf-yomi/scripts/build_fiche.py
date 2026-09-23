#!/usr/bin/env python3
"""Assemble les deux fiches d'un daf : <slug>.source.json (collecte) +
<slug>.fr.json (francais redige par Claude) -> Markdown, HTML et PDF.

  python3 scripts/build_fiche.py --jour 2026-09-23
  python3 scripts/build_fiche.py "Bekhorot 5" --only light

Deux documents par daf :
  <slug>_B.md/.html/.pdf        lecture guidee complete, traduction integrale
  <slug>_B-light.md/.html/.pdf  structure et exposé, plafonne a 6 pages

Garde-fous — le script refuse d'assembler plutot que de livrer du faux :
  1. l'arameen n'est JAMAIS saisi dans le .fr.json : il est lu depuis la
     collecte. Une citation ne peut donc pas etre inexacte.
  2. B exige une traduction pour chaque segment de chaque amoud.
  3. B-light est plafonne a 6 pages.
  4. un PDF contenant une page d'erreur de navigateur est rejete.
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
import daf_calendar as C  # noqa: E402
import render as R  # noqa: E402

paths.ensure()

PLAFOND_PAGES_LIGHT = 6
CAR_PAR_PAGE = 2600          # estimation avant rendu
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = {0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi", 4: "vendredi",
         5: "samedi", 6: "dimanche"}


def slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def date_fr(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month - 1]} {d.year}"


def charge(slug: str) -> tuple[dict, dict]:
    sp = os.path.join(paths.FICHES, slug + ".source.json")
    fp = os.path.join(paths.FICHES, slug + ".fr.json")
    if not os.path.exists(sp):
        raise SystemExit(f"collecte absente : lancer\n"
                         f"  python3 scripts/fetch_daf.py \"{slug.replace('_', ' ')}\"")
    if not os.path.exists(fp):
        raise SystemExit(f"francais absent : {os.path.relpath(fp, paths.HOME)}\n"
                         f"  (c'est a Claude de le rediger — cf. skill daf-fiche)")
    with open(sp, encoding="utf-8") as fh:
        src = json.load(fh)
    with open(fp, encoding="utf-8") as fh:
        fr = json.load(fh)
    return src, fr


# ------------------------------------------------------------------ controles
def controle_traduction(src: dict, fr: dict) -> list[str]:
    errs = []
    trad = fr.get("traduction") or {}
    for cle, a in src["amudim"].items():
        got = trad.get(cle) or []
        if len(got) != a["n_segments"]:
            errs.append(f"traduction {cle} : {len(got)} segments traduits "
                        f"sur {a['n_segments']}")
        vides = [i + 1 for i, s in enumerate(got) if not str(s).strip()]
        if vides:
            errs.append(f"traduction {cle} : segments vides {vides}")
    return errs


def controle_citations(src: dict, fr: dict) -> list[str]:
    """Verifie que chaque citation pointe un segment existant."""
    errs = []
    for s in fr.get("sugyot", []):
        for c in s.get("citations", []):
            a = src["amudim"].get(c.get("amud"))
            if not a:
                errs.append(f"sugya {s.get('n')} : amoud inconnu {c.get('amud')!r}")
                continue
            i = int(c.get("seg", 0))
            if not (1 <= i <= a["n_segments"]):
                errs.append(f"sugya {s.get('n')} : segment {c.get('amud')}:{i} "
                            f"hors bornes (1..{a['n_segments']})")
    return errs


def controle_difficultes(fr: dict) -> list[str]:
    n = sum(1 for s in fr.get("sugyot", []) if s.get("difficulte"))
    if n > 1:
        return [f"{n} difficultes retenues : le plafond est de 1 (les autres "
                f"vont dans difficultes_en_renvoi)"]
    return []


# --------------------------------------------------------------------- rendus
def entete(src: dict, fr: dict, date_iso: str | None) -> list[str]:
    L = [f"# {src['traite_fr']} {src['daf']}", ""]
    ligne = [f"**Daf Yomi** · {src['traite_fr']} {src['daf']} "
             f"sur {src['dernier_daf']} · seder {src['seder']}"]
    if date_iso:
        ligne.insert(0, f"**{date_fr(date_iso)}**")
    # Markdown fusionne des lignes consecutives en un seul paragraphe : chaque
    # ligne d'en-tete se termine donc par deux espaces (saut de ligne force).
    L.append(" · ".join(ligne) + "  ")
    cyc = C.siyoum()
    if cyc.get("fin") and date_iso:
        reste = (dt.date.fromisoformat(cyc["fin"])
                 - dt.date.fromisoformat(date_iso)).days
        L.append(f"**Siyoum haShas** le {cyc['fin']} ({cyc.get('dernier')}) — "
                 f"dans {reste} jours  ")
    if fr.get("titre_court"):
        L += ["", f"*{fr['titre_court']}*"]
    L += ["", "---", ""]
    return L


def bloc_citation(src: dict, c: dict) -> str:
    """L'arameen vient de la collecte : il ne peut pas etre inexact."""
    a = src["amudim"][c["amud"]]
    he = a["he"][int(c["seg"]) - 1]
    return (f"> {he}\n>\n> *{c['amud']}:{c['seg']}* — "
            f"{c.get('rendu', '').strip()}\n")


def bloc_tableau(t: dict) -> list[str]:
    L = []
    if t.get("titre"):
        L.append(f"**{t['titre']}**")
        L.append("")
    cols = t.get("colonnes") or []
    L.append("| " + " | ".join(str(c) for c in cols) + " |")
    L.append("|" + "|".join(["---"] * len(cols)) + "|")
    for r in t.get("lignes") or []:
        L.append("| " + " | ".join(str(x) for x in r) + " |")
    L.append("")
    return L


def bloc_difficulte(d: dict) -> list[str]:
    L = ["### La difficulté", "", f"**{d.get('titre', '').strip()}**", ""]
    if d.get("question"):
        L += [d["question"].strip(), ""]
    if d.get("reponses"):
        L.append("**Réponses**")
        L.append("")
        for r in d["reponses"]:
            L.append(f"- {r}")
        L.append("")
    return L


def sources(src: dict) -> list[str]:
    L = ["---", "", "### Sources", ""]
    L.append("Texte : " + " · ".join(
        f"[{k}]({v['url']})" for k, v in src["amudim"].items()))
    if src["sources"].get("background"):
        L.append(f"Notions de fond et variantes : "
                 f"[Background, Kollel Iyun Hadaf]({src['sources']['background']})")
    if src["sources"].get("insights"):
        L.append(f"Difficultés : "
                 f"[Insights, Kollel Iyun Hadaf]({src['sources']['insights']})")
    L += ["", "> L'araméen est reproduit tel quel depuis Sefaria."]
    return L


def md_B(src: dict, fr: dict, date_iso: str | None) -> str:
    L = entete(src, fr, date_iso)
    L += ["> **Lecture guidée.** Le texte du daf est traduit intégralement, "
          "organisé par sugya.", ""]
    trad = fr.get("traduction") or {}
    for s in fr.get("sugyot", []):
        L += [f"## {s['n']}. {s['titre']}", "",
              f"*{s.get('loc', '')}"
              + (f" · {s['nature']}*" if s.get("nature") else "*"), ""]
        if s.get("intro"):
            L += [s["intro"].strip(), ""]
        for c in s.get("citations", []):
            L += [bloc_citation(src, c), ""]
        for t in s.get("tableaux", []):
            L += bloc_tableau(t)
        if s.get("difficulte"):
            L += bloc_difficulte(s["difficulte"])
    L += ["---", "", "## Le texte, traduit intégralement", ""]
    for cle, a in src["amudim"].items():
        L += [f"### {cle}", ""]
        for i, he in enumerate(a["he"], 1):
            L += [f"> {he}", "", f"**{cle}:{i}** — {trad[cle][i - 1]}", ""]
    for nom in ("Rashi", "Tosafot"):
        items = [x for cle, v in src["commentateurs"].items()
                 if cle != "_erreurs" for x in v.get(nom, [])]
        if items:
            L += [f"## {nom} — {len(items)} dibbourim", ""]
            for x in items:
                L += [f"> {x['he']}", "", f"*{x['ancre']}*", ""]
    if fr.get("glossaire"):
        L += ["## Notions de fond", "", "| terme | ligne | sens |",
              "|---|---|---|"]
        for g in fr["glossaire"]:
            L.append(f"| {g.get('he','')} | {g.get('ligne','')} | {g.get('sens','')} |")
        L.append("")
    if fr.get("girsa"):
        L += ["## Variantes textuelles", ""] + [f"- {g}" for g in fr["girsa"]] + [""]
    L += sources(src)
    return "\n".join(L)


def md_B_light(src: dict, fr: dict, date_iso: str | None) -> str:
    L = entete(src, fr, date_iso)
    if fr.get("avant_douvrir"):
        L += ["## Ce qu'il faut savoir avant d'ouvrir", "",
              fr["avant_douvrir"].strip(), ""]
    L += ["## Carte du daf", "", "| # | sugya | où | nature |", "|---|---|---|---|"]
    for s in fr.get("sugyot", []):
        L.append(f"| {s['n']} | {s['titre']} | {s.get('loc','')} | "
                 f"{s.get('nature','')} |")
    L.append("")
    for s in fr.get("sugyot", []):
        L += ["---", "", f"## {s['n']}. {s['titre']}", "",
              f"*{s.get('loc','')}"
              + (f" · {s['nature']}*" if s.get("nature") else "*"), ""]
        if s.get("expose"):
            L += [s["expose"].strip(), ""]
        for c in s.get("citations", []):
            L += [bloc_citation(src, c), ""]
        for t in s.get("tableaux", []):
            L += bloc_tableau(t)
        if s.get("difficulte"):
            L += bloc_difficulte(s["difficulte"])
    if fr.get("difficultes_en_renvoi"):
        L += ["*Autres difficultés disponibles sur ce daf, non reprises ici : "
              + " ; ".join(fr["difficultes_en_renvoi"]) + ".*", ""]
    if fr.get("glossaire"):
        L += ["---", "", "## Notions de fond", "", "| terme | ligne | sens |",
              "|---|---|---|"]
        for g in fr["glossaire"]:
            L.append(f"| {g.get('he','')} | {g.get('ligne','')} | {g.get('sens','')} |")
        L.append("")
    if fr.get("a_retenir"):
        L += ["## À retenir", ""] + [f"- {x}" for x in fr["a_retenir"]] + [""]
    L += sources(src)
    L += ["", "> **Le français est un exposé, non une traduction.** Pour le "
          "texte intégral traduit, voir la version B."]
    return "\n".join(L)


# ----------------------------------------------------------------------- main
def produit(slug: str, date_iso: str | None, only: str | None, pdf: bool):
    src, fr = charge(slug)
    errs = controle_citations(src, fr) + controle_difficultes(fr)
    if only != "light":
        errs += controle_traduction(src, fr)
    if errs:
        raise SystemExit("assemblage refusé pour " + slug + " :\n  - "
                         + "\n  - ".join(errs))

    cibles = []
    if only in (None, "B"):
        cibles.append(("B", md_B(src, fr, date_iso), None))
    if only in (None, "light"):
        cibles.append(("B-light", md_B_light(src, fr, date_iso),
                       PLAFOND_PAGES_LIGHT))

    for nom, texte, plafond in cibles:
        base = os.path.join(paths.FICHES, f"{slug}_{nom}")
        with open(base + ".md", "w", encoding="utf-8") as fh:
            fh.write(texte)
        est = len(texte) / CAR_PAR_PAGE
        if plafond and est > plafond + 0.6:
            raise SystemExit(
                f"{nom} : ~{est:.1f} pages estimées, plafond {plafond}. "
                f"Réduire — une seule difficulté, un tableau plutôt que de la "
                f"prose, moins de citations.")
        print(f"  {nom:8s} {len(texte):6d} car.  ~{est:.1f} pages"
              f"  -> {os.path.basename(base)}.md")
        if not pdf:
            continue
        R.md_to_html(base + ".md", base + ".html")
        ok, info = R.html_to_pdf(base + ".html", base + ".pdf")
        if not ok:
            print(f"    PDF non généré : {info}")
            continue
        n = pages_pdf(base + ".pdf")
        print(f"    -> {os.path.basename(base)}.pdf  "
              f"{os.path.getsize(base + '.pdf') // 1024} Ko"
              + (f", {n} pages" if n else ""))
        if plafond and n and n > plafond:
            print(f"    ATTENTION : {n} pages, plafond {plafond}")


def pages_pdf(p: str) -> int | None:
    import subprocess
    try:
        out = subprocess.run(["mdls", "-name", "kMDItemNumberOfPages", p],
                             capture_output=True, text=True, timeout=20).stdout
        m = re.search(r"=\s*(\d+)", out)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("libelle", nargs="?")
    ap.add_argument("--jour")
    ap.add_argument("--only", choices=["B", "light"])
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()

    if a.jour:
        d = C.jour(a.jour)
        if not d:
            raise SystemExit(f"aucun daf au {a.jour}")
        slug, date_iso = slugify(d["libelle"]), a.jour
    elif a.libelle:
        slug, date_iso = slugify(a.libelle), None
    else:
        raise SystemExit("donner un libelle ou --jour AAAA-MM-JJ")
    print(slug.replace("_", " "))
    produit(slug, date_iso, a.only, not a.no_pdf)


if __name__ == "__main__":
    main()
