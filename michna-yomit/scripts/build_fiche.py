#!/usr/bin/env python3
"""Assemble la fiche d'une michna : <slug>.source.json (Sefaria) + <slug>.fr.json
(francais redige par Claude) -> Markdown, HTML et PDF.

  python3 scripts/build_fiche.py "Mishnah Oholot 2:4"
  python3 scripts/build_fiche.py --day 2026-09-17            # les 2 du jour
  python3 scripts/build_fiche.py --day 2026-09-17 --pdf-only

Le script n'invente aucun contenu : il refuse d'assembler si une section du
Bartenura n'a pas sa traduction francaise.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

paths.ensure()
ROOT = paths.HOME
FICHES = paths.FICHES
DATA = paths.DATA

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = {0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi", 4: "vendredi",
         5: "samedi", 6: "dimanche"}

# Chemins macOS (application) puis binaires a chercher dans le PATH. Les
# conteneurs Linux — dont celui de Claude Cowork — ont Chromium dans le PATH
# et aucun /Applications : ne chercher que sur macOS faisait silencieusement
# tomber la generation sur wkhtmltopdf, qui tronque l'hebreu.
CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
CHROME_BINARIES = [
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
    "chrome", "brave-browser", "microsoft-edge", "headless_shell",
]


def find_chrome() -> str | None:
    """Premier navigateur disponible : $MICHNA_CHROME, une app macOS, ou un
    binaire du PATH (Linux)."""
    env = os.environ.get("MICHNA_CHROME")
    if env and (os.path.exists(env) or shutil.which(env)):
        return env if os.path.exists(env) else shutil.which(env)
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    for b in CHROME_BINARIES:
        found = shutil.which(b)
        if found:
            return found
    return None


def slugify(ref: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", ref).strip("_")


def date_fr(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month - 1]} {d.year}"


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def day_for_ref(ref: str):
    cal = load_json(os.path.join(DATA, "calendar.json"))
    for d in cal["days"]:
        if ref in d["refs"]:
            return d, cal
    return None, cal


# --------------------------------------------------------------------------- MD

def build_md(src: dict, fr: dict) -> str:
    ref = src["ref"]
    day, cal = day_for_ref(ref)
    L = []
    L.append(f"# {src['tractate_fr']} {ref.rsplit(' ', 1)[1]}")
    L.append("")
    meta = [f"**Traité** : {src['tractate_fr']} ({src['seder_fr']})",
            f"**Référence** : `{ref}` — {src['ref_he']}"]
    if day:
        meta.append(f"**Programme** : jour {day['day']} / {cal['n_days']} — "
                    f"{date_fr(day['date'])}")
    if fr.get("titre_court"):
        meta.append(f"**Sujet** : {fr['titre_court']}")
    L += meta + [""]
    L.append("---")
    L.append("")

    L.append("## 1. Texte hébreu")
    L.append("")
    L.append(f"> {src['michna']['hebreu']}")
    L.append("")
    L.append(f"*Source : [Sefaria]({src['sources']['michna']}) — "
             f"édition Torat Emet / Vilna.*")
    L.append("")

    L.append("## 2. Traduction française")
    L.append("")
    L.append(fr["traduction"])
    L.append("")

    if fr.get("explication"):
        L.append("## 3. Explication")
        L.append("")
        for para in fr["explication"]:
            L.append(para)
            L.append("")

    if fr.get("contexte"):
        L.append("### Contexte")
        L.append("")
        L.append(fr["contexte"])
        L.append("")

    secs = src["bartenura"]["sections"]
    frb = {int(b["n"]): b for b in fr.get("bartenura", [])}
    L.append(f"## 4. Bartenura — {len(secs)} section"
             f"{'s' if len(secs) > 1 else ''} (intégral)")
    L.append("")
    for s in secs:
        n = s["n"]
        lemme = s["lemme_he"] or s["lemme_en"] or f"section {n}"
        L.append(f"### {n}. {lemme}")
        L.append("")
        L.append(f"**Hébreu** — {s['hebreu']}")
        L.append("")
        t = frb.get(n, {}).get("traduction", "")
        L.append(f"**Français** — {t}")
        L.append("")
        if frb.get(n, {}).get("note"):
            L.append(f"*Note : {frb[n]['note']}*")
            L.append("")
    if src["bartenura"]["ref"]:
        L.append(f"*Source : [Sefaria — {src['bartenura']['ref']}]"
                 f"({src['sources']['bartenura']}).*")
        L.append("")

    tal = src["talmud"]
    if tal["refs"]:
        L.append("## 5. Renvois Talmud")
        L.append("")
        for r in tal["refs"]:
            dy = next((x for x in tal["dafyomi"] if x["ref"] == r), None)
            line = f"- **{r}**"
            if dy:
                line += (f" — [background dafyomi.co.il]({dy['background_url']})"
                         f" · [insights]({dy['insights_url']})")
            L.append(line)
        L.append("")

    if fr.get("points_essentiels"):
        L.append("## 6. Points essentiels")
        L.append("")
        for p in fr["points_essentiels"]:
            L.append(f"- {p}")
        L.append("")

    L.append("---")
    L.append("")
    L.append("### Sources")
    L.append("")
    L.append(f"- Michna (hébreu + anglais) : {src['sources']['michna']}")
    if src["sources"]["bartenura"]:
        L.append(f"- Bartenura : {src['sources']['bartenura']}")
    L.append(f"- Explication anglaise (Dr. Joshua Kulp) : "
             f"{src['sources']['explication_kulp']}")
    L.append("")
    L.append("> La traduction et l'explication en français sont rédigées d'après "
             "ces sources. Les textes hébreux sont reproduits tels quels depuis "
             "Sefaria ; le français n'est pas une source Sefaria.")
    L.append("")
    return "\n".join(L)


# ------------------------------------------------------------------------- HTML

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "Times New Roman", Times, serif; font-size: 11.5pt;
       line-height: 1.55; color: #1a1a1a; max-width: 760px; margin: 0 auto; }
/* A l'impression, la zone utile d'une A4 avec les marges @page fait ~673 px a
   96 dpi : un max-width de 760 px depasse de ~87 px. Chrome recale, mais
   wkhtmltopdf laisse deborder — et un bloc RTL aligne a droite voit alors son
   DEBUT sortir de la page et se faire couper. */
@media print { body { max-width: 100%; margin: 0; } }
h1 { font-size: 20pt; margin: 0 0 4pt; border-bottom: 2px solid #8a6d3b;
     padding-bottom: 6pt; }
h2 { font-size: 14pt; margin: 22pt 0 8pt; color: #6b4f1d;
     border-bottom: 1px solid #ddd; padding-bottom: 3pt; }
h3 { font-size: 12pt; margin: 14pt 0 5pt; color: #333; }
.meta { font-size: 10pt; color: #555; margin-bottom: 14pt; }
.meta div { margin: 2pt 0; }
blockquote, .he, .bart .lemme { direction: rtl; text-align: right;
  /* `embed` d'abord : les moteurs anciens (Qt WebKit de wkhtmltopdf) ignorent
     `isolate` et prendraient la declaration entiere en defaut. */
  unicode-bidi: embed; unicode-bidi: isolate;
  /* Le repli doit etre explicite : sans cela wkhtmltopdf ne coupe pas une
     longue ligne hebraique et la fait deborder. */
  overflow-wrap: break-word; word-wrap: break-word; white-space: normal;
  max-width: 100%; box-sizing: border-box; }
blockquote, .he {
  font-family: "Times New Roman", "Arial Hebrew", "SF Hebrew", "FreeSerif", serif;
  font-size: 14pt; line-height: 1.9; background: #faf7f0;
  border-right: 3px solid #8a6d3b; padding: 10pt 12pt; margin: 8pt 0; }
.bart { margin: 0 0 12pt; padding-bottom: 8pt; border-bottom: 1px dotted #ccc; }
.bart .lemme { font-weight: bold; font-size: 12.5pt;
  font-family: "Times New Roman", "Arial Hebrew", "FreeSerif", serif; }
.bart .he { font-size: 12.5pt; line-height: 1.8; background: #fcfaf5;
  padding: 7pt 10pt; }
.bart .fr { margin-top: 5pt; }
.bart .fr b, .bart .he-label { color: #6b4f1d; }
ul { margin: 6pt 0 6pt 16pt; } li { margin: 3pt 0; }
a { color: #1a5a8a; text-decoration: none; }
.footer { margin-top: 20pt; padding-top: 8pt; border-top: 1px solid #ddd;
  font-size: 9pt; color: #666; }
.note { font-style: italic; color: #555; font-size: 10pt; }
"""


EMPH_STRONG = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", re.S)
EMPH_ITALIC = re.compile(r"(?<!\*)\*(?=\S)([^*]+?)(?<=\S)\*(?!\*)", re.S)


def rich(s) -> str:
    """Echappe le HTML puis rend l'emphase Markdown. Le francais des fiches
    est redige avec la convention Markdown (`*terme*` pour un terme
    translittere) : sans cette conversion, les asterisques s'affichaient
    litteralement dans le HTML et le PDF."""
    import html as H
    out = H.escape(s or "")
    out = EMPH_STRONG.sub(r"<strong>\1</strong>", out)
    out = EMPH_ITALIC.sub(r"<em>\1</em>", out)
    return out


def build_html(src: dict, fr: dict) -> str:
    import html as H
    e = H.escape
    ref = src["ref"]
    day, cal = day_for_ref(ref)
    P = []
    P.append(f"<h1>{e(src['tractate_fr'])} {e(ref.rsplit(' ', 1)[1])}</h1>")
    P.append('<div class="meta">')
    P.append(f"<div><b>Traité</b> : {e(src['tractate_fr'])} "
             f"({e(src['seder_fr'])})</div>")
    P.append(f"<div><b>Référence</b> : {e(ref)} — "
             f'<span class="he" style="background:none;border:none;padding:0;'
             f'font-size:11pt">{e(src["ref_he"])}</span></div>')
    if day:
        P.append(f"<div><b>Programme</b> : jour {day['day']} / {cal['n_days']} — "
                 f"{e(date_fr(day['date']))}</div>")
    if fr.get("titre_court"):
        P.append(f"<div><b>Sujet</b> : {rich(fr['titre_court'])}</div>")
    P.append("</div>")

    P.append("<h2>1. Texte hébreu</h2>")
    P.append(f'<div class="he">{e(src["michna"]["hebreu"])}</div>')
    P.append(f'<p class="note">Source : Sefaria — édition Torat Emet / Vilna.</p>')

    P.append("<h2>2. Traduction française</h2>")
    for para in fr["traduction"].split("\n\n"):
        P.append(f"<p>{rich(para)}</p>")

    if fr.get("explication"):
        P.append("<h2>3. Explication</h2>")
        for para in fr["explication"]:
            P.append(f"<p>{rich(para)}</p>")
    if fr.get("contexte"):
        P.append("<h3>Contexte</h3>")
        P.append(f"<p>{rich(fr['contexte'])}</p>")

    secs = src["bartenura"]["sections"]
    frb = {int(b["n"]): b for b in fr.get("bartenura", [])}
    P.append(f"<h2>4. Bartenura — {len(secs)} section"
             f"{'s' if len(secs) > 1 else ''} (intégral)</h2>")
    for s in secs:
        n = s["n"]
        P.append('<div class="bart">')
        lemme = s["lemme_he"] or s["lemme_en"]
        if lemme:
            P.append(f'<div class="lemme">{n}. {e(lemme)}</div>')
        else:
            P.append(f"<h3>Section {n}</h3>")
        P.append(f'<div class="he">{e(s["hebreu"])}</div>')
        P.append(f'<div class="fr"><b>Français</b> — '
                 f'{rich(frb.get(n, {}).get("traduction", ""))}</div>')
        if frb.get(n, {}).get("note"):
            P.append(f'<div class="note">Note : {rich(frb[n]["note"])}</div>')
        P.append("</div>")

    tal = src["talmud"]
    if tal["refs"]:
        P.append("<h2>5. Renvois Talmud</h2><ul>")
        for r in tal["refs"]:
            dy = next((x for x in tal["dafyomi"] if x["ref"] == r), None)
            li = f"<li><b>{e(r)}</b>"
            if dy:
                li += (f' — <a href="{e(dy["background_url"])}">background '
                       f'dafyomi.co.il</a>')
            P.append(li + "</li>")
        P.append("</ul>")

    if fr.get("points_essentiels"):
        P.append("<h2>6. Points essentiels</h2><ul>")
        for p in fr["points_essentiels"]:
            P.append(f"<li>{rich(p)}</li>")
        P.append("</ul>")

    P.append('<div class="footer">')
    P.append(f'Sources : <a href="{e(src["sources"]["michna"])}">Michna</a>')
    if src["sources"]["bartenura"]:
        P.append(f' · <a href="{e(src["sources"]["bartenura"])}">Bartenura</a>')
    P.append(f' · <a href="{e(src["sources"]["explication_kulp"])}">'
             f'explication anglaise (Dr. J. Kulp)</a>.<br>')
    P.append("Les textes hébreux sont reproduits depuis Sefaria. La traduction "
             "et l'explication françaises sont rédigées d'après ces sources ; "
             "elles ne sont pas une source Sefaria.")
    P.append("</div>")

    return ("<!DOCTYPE html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
            f"<title>{e(src['tractate_fr'])} {e(ref.rsplit(' ', 1)[1])}</title>"
            f"<style>{CSS}</style></head><body>" + "\n".join(P) +
            "</body></html>")


# -------------------------------------------------------------------------- PDF

def html_to_pdf(html_path: str, pdf_path: str) -> tuple[bool, str]:
    chrome = find_chrome()
    if chrome:
        # Profil persistant hors du plugin : le premier lancement de Chrome
        # coute environ une minute, le reutiliser accelere les suivants. Il
        # pese ~100 Mo, donc il ne va pas dans le dossier du plugin.
        prof = os.path.join(tempfile.gettempdir(), "michna-yomit-chrome")
        os.makedirs(prof, exist_ok=True)
        try:
            r = subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--no-sandbox",
                 "--no-first-run", "--no-default-browser-check",
                 "--disable-extensions", "--disable-sync",
                 "--virtual-time-budget=3000",
                 f"--user-data-dir={prof}", "--no-pdf-header-footer",
                 f"--print-to-pdf={pdf_path}", "file://" + html_path],
                capture_output=True, timeout=240)
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
                return True, os.path.basename(chrome)
            return False, (r.stderr.decode()[-300:] or "chrome: PDF vide")
        except Exception as exc:
            return False, f"chrome: {exc}"

    if shutil.which("weasyprint"):
        try:
            subprocess.run(["weasyprint", html_path, pdf_path],
                           capture_output=True, timeout=180, check=True)
            if os.path.exists(pdf_path):
                return True, "weasyprint"
        except Exception as exc:
            return False, f"weasyprint: {exc}"
    if shutil.which("wkhtmltopdf"):
        # Sans geometrie explicite, wkhtmltopdf applique ses propres marges et
        # ignore @page : la mise en page deborde et l'hebreu se fait couper.
        try:
            subprocess.run(
                ["wkhtmltopdf", "--quiet", "--encoding", "utf-8",
                 "--page-size", "A4", "--print-media-type",
                 "--margin-top", "18mm", "--margin-bottom", "18mm",
                 "--margin-left", "16mm", "--margin-right", "16mm",
                 "--enable-local-file-access",
                 html_path, pdf_path],
                capture_output=True, timeout=180, check=True)
            if os.path.exists(pdf_path):
                return True, "wkhtmltopdf"
        except Exception as exc:
            return False, f"wkhtmltopdf: {exc}"
    return False, ("aucun convertisseur : installer Google Chrome, "
                   "`pip install weasyprint` ou `brew install wkhtmltopdf`")


# ------------------------------------------------------------------------- main

def check_fr(src: dict, fr: dict) -> list[str]:
    errs = []
    if not fr.get("traduction", "").strip():
        errs.append("`traduction` manquante")
    n = src["bartenura"]["n_sections"]
    frb = {int(b["n"]) for b in fr.get("bartenura", []) if b.get("traduction", "").strip()}
    missing = [i for i in range(1, n + 1) if i not in frb]
    if missing:
        errs.append(f"traduction du Bartenura manquante pour les sections "
                    f"{', '.join(map(str, missing))} (sur {n})")
    return errs


def one(ref: str, pdf: bool = True, md: bool = True) -> None:
    slug = slugify(ref)
    sp = os.path.join(FICHES, slug + ".source.json")
    fp = os.path.join(FICHES, slug + ".fr.json")
    if not os.path.exists(sp):
        raise SystemExit(f"source absente : lancer d'abord\n"
                         f"  python3 scripts/fetch_mishna.py \"{ref}\"")
    if not os.path.exists(fp):
        raise SystemExit(f"francais absent : {os.path.relpath(fp, ROOT)}\n"
                         f"  (c'est a Claude de le rediger, cf. skill michna-fiche)")
    src, fr = load_json(sp), load_json(fp)
    errs = check_fr(src, fr)
    if errs:
        raise SystemExit("fiche incomplete pour " + ref + " :\n  - " +
                         "\n  - ".join(errs))

    outs = []
    if md:
        mdp = os.path.join(FICHES, slug + ".md")
        with open(mdp, "w", encoding="utf-8") as fh:
            fh.write(build_md(src, fr))
        outs.append(mdp)
    htmlp = os.path.join(FICHES, slug + ".html")
    with open(htmlp, "w", encoding="utf-8") as fh:
        fh.write(build_html(src, fr))
    outs.append(htmlp)
    if pdf:
        pdfp = os.path.join(FICHES, slug + ".pdf")
        ok, info = html_to_pdf(htmlp, pdfp)
        if ok:
            outs.append(pdfp)
        else:
            print(f"  PDF non genere ({info})")
    for o in outs:
        print(f"  -> {os.path.relpath(o, ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref", nargs="?")
    ap.add_argument("--day")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--pdf-only", action="store_true")
    a = ap.parse_args()

    refs = []
    if a.day:
        cal = load_json(os.path.join(DATA, "calendar.json"))
        refs = next((d["refs"] for d in cal["days"] if d["date"] == a.day), [])
        if not refs:
            raise SystemExit(f"aucun jour de programme au {a.day}")
    elif a.ref:
        refs = [a.ref]
    else:
        raise SystemExit("donner une ref ou --day AAAA-MM-JJ")
    for ref in refs:
        print(ref)
        one(ref, pdf=not a.no_pdf, md=not a.pdf_only)


if __name__ == "__main__":
    main()
