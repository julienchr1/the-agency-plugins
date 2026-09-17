#!/usr/bin/env python3
"""Rassemble TOUT le materiel source d'une michna depuis Sefaria.

  python3 scripts/fetch_mishna.py "Mishnah Oktzin 3:6"
  python3 scripts/fetch_mishna.py --day 2026-09-17     # les michnaiot du jour

Ecrit fiches/<slug>.source.json : texte hebreu, traductions anglaises,
l'explication de Kulp, TOUTES les sections du Bartenura (hebreu + anglais
alignes) et les renvois Talmud/daf yomi. Aucun contenu n'est genere ici :
c'est de la collecte sourcee, destinee a etre traduite ensuite.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402
import sefaria  # noqa: E402

paths.ensure()
ROOT = paths.HOME
FICHES = paths.FICHES
DATA = paths.DATA

TAG_RE = re.compile(r"<[^>]+>")
BOLD_RE = re.compile(r"<b>(.*?)</b>", re.S | re.I)
FOOTNOTE_RE = re.compile(r"<i\s+data-commentator[^>]*>.*?</i>", re.S | re.I)
SUP_RE = re.compile(r"<sup>.*?</sup>\s*<i\s+class=[\"']footnote[\"']>.*?</i>", re.S | re.I)


def clean(s) -> str:
    """Retire le balisage Sefaria en preservant le texte."""
    if s is None:
        return ""
    if isinstance(s, list):
        return "\n".join(clean(x) for x in s)
    s = SUP_RE.sub("", s)
    s = FOOTNOTE_RE.sub("", s)
    s = s.replace("<br>", " ").replace("<br/>", " ")
    s = TAG_RE.sub("", s)
    s = html.unescape(s)
    return re.sub(r"[ \t]+", " ", s).strip()


def _split_outside_parens(txt: str):
    """Coupe sur le premier tiret separateur situe hors parentheses."""
    depth = 0
    for i, ch in enumerate(txt):
        if ch in "([\u201c\u2018":
            depth += 1
        elif ch in ")]\u201d\u2019":
            depth = max(0, depth - 1)
        elif depth == 0 and ch in "-\u2013\u2014":
            before, after = txt[:i], txt[i + 1:]
            if after.startswith(" "):
                return before.strip(), after.strip()
    return None


def split_lemma(seg: str) -> dict:
    """Un segment de Bartenura = <b>lemme de la michna</b> + commentaire.

    L'hebreu balise le lemme en <b>. L'anglais utilise la forme
    "lemme hebreu (glose) - commentaire" : on coupe sur le tiret, mais
    jamais a l'interieur d'une parenthese.
    """
    if seg is None:
        seg = ""
    m = BOLD_RE.search(seg)
    if m:
        lemma = clean(m.group(1))
        rest = clean(seg[m.end():])
        return {"lemme": lemma.rstrip(".:"), "texte": rest}
    txt = clean(seg)
    if re.search(r"[\u0590-\u05FF]", txt[:160]):
        cut = _split_outside_parens(txt)
        if cut and len(cut[0]) <= 160:
            return {"lemme": cut[0].rstrip(".:"), "texte": cut[1]}
    return {"lemme": "", "texte": txt}


def as_list(x) -> list:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def fetch_version(ref: str, version: str | None):
    try:
        return sefaria.text(ref, version=version)
    except Exception as exc:
        return {"error": str(exc)}


def bavli_refs(ref: str) -> list[str]:
    """Renvoie les folios du Talmud Bavli lies a cette michna."""
    try:
        lk = sefaria.links(ref)
    except Exception:
        return []
    out = []
    for l in lk:
        if l.get("category") != "Talmud":
            continue
        r = l.get("ref", "")
        # on ne garde que "Traite 12a", pas les commentaires ni le Yerushalmi
        if re.fullmatch(r"[A-Z][A-Za-z' ]+ \d+[ab]", r):
            out.append(r)
    seen, uniq = set(), []
    for r in out:
        if r not in seen:
            seen.add(r)
            uniq.append(r)
    return uniq


def dafyomi_links(refs: list[str]) -> list[dict]:
    path = os.path.join(DATA, "dafyomi_slugs.json")
    if not os.path.exists(path):
        return []
    slugs = json.load(open(path, encoding="utf-8"))["tractates"]
    out = []
    for r in refs:
        m = re.fullmatch(r"([A-Za-z' ]+) (\d+)([ab])", r)
        if not m:
            continue
        name, daf = m.group(1).strip(), int(m.group(2))
        info = slugs.get(name)
        if not info:
            continue
        url = (f"https://www.dafyomi.co.il/{info['slug']}/backgrnd/"
               f"{info['prefix']}-in-{daf:03d}.htm")
        out.append({"ref": r, "daf": daf, "background_url": url,
                    "insights_url": url.replace("/backgrnd/", "/insites/")
                                        .replace("-in-", "-dt-")})
    seen, uniq = set(), []
    for o in out:
        if o["background_url"] not in seen:
            seen.add(o["background_url"])
            uniq.append(o)
    return uniq


def tractate_of(ref: str) -> str:
    return ref.rsplit(" ", 1)[0]


def bartenura_ref(ref: str) -> str | None:
    idx = json.load(open(os.path.join(DATA, "tractates.json"), encoding="utf-8"))
    byt = {t["title"]: t for t in idx["tractates"]}
    t = byt.get(tractate_of(ref))
    if not t or not t.get("bartenura_title"):
        return None
    return ref.replace(tractate_of(ref), t["bartenura_title"])


def collect(ref: str) -> dict:
    idx = json.load(open(os.path.join(DATA, "tractates.json"), encoding="utf-8"))
    byt = {t["title"]: t for t in idx["tractates"]}
    tract = byt.get(tractate_of(ref))
    if not tract:
        raise SystemExit(f"traite inconnu dans {ref!r}")

    # --- Michna : hebreu + anglais
    base = fetch_version(ref, None)
    he = clean(base.get("he"))
    en_davidson = clean(base.get("text"))
    kulp_tr = fetch_version(ref, "Mishnah Yomit by Dr. Joshua Kulp")
    en_kulp = clean(kulp_tr.get("text")) if "error" not in kulp_tr else ""

    # --- Explication de Kulp (commentaire suivi)
    expl_ref = ref.replace(tractate_of(ref), f"English Explanation of {tractate_of(ref)}")
    expl = fetch_version(expl_ref, None)
    explanation = [clean(s) for s in as_list(expl.get("text")) if clean(s)]

    # --- Bartenura : toutes les sections
    bref = bartenura_ref(ref)
    bart_he, bart_en, sections = [], [], []
    if bref:
        bd = fetch_version(bref, None)
        bart_he = as_list(bd.get("he"))
        bart_en = as_list(bd.get("text"))
        n = max(len(bart_he), len(bart_en))
        for i in range(n):
            h = split_lemma(bart_he[i] if i < len(bart_he) else "")
            e = split_lemma(bart_en[i] if i < len(bart_en) else "")
            sections.append({
                "n": i + 1,
                "lemme_he": h["lemme"],
                "hebreu": h["texte"],
                "lemme_en": e["lemme"],
                "anglais": e["texte"],
            })

    tal = bavli_refs(ref)
    return {
        "ref": ref,
        "ref_he": f"{tract['he_title']} {ref.rsplit(' ', 1)[1]}",
        "tractate": tract["title"],
        "tractate_fr": tract["name_fr"],
        "seder_fr": tract["seder_fr"],
        "sources": {
            "michna": sefaria.sefaria_url(ref),
            "bartenura": sefaria.sefaria_url(bref) if bref else None,
            "explication_kulp": sefaria.sefaria_url(expl_ref),
        },
        "michna": {
            "hebreu": he,
            "anglais_davidson": en_davidson,
            "anglais_kulp": en_kulp,
        },
        "explication_kulp": explanation,
        "bartenura": {
            "ref": bref,
            "n_sections": len(sections),
            "sections": sections,
        },
        "talmud": {
            "refs": tal,
            "dafyomi": dafyomi_links(tal),
        },
    }


def slugify(ref: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", ref).strip("_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref", nargs="?")
    ap.add_argument("--day", help="date ISO : recupere les michnaiot du programme ce jour-la")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    refs = []
    if args.day:
        cal = json.load(open(os.path.join(DATA, "calendar.json"), encoding="utf-8"))
        for d in cal["days"]:
            if d["date"] == args.day:
                refs = d["refs"]
                break
        if not refs:
            raise SystemExit(f"aucun jour de programme au {args.day}")
    elif args.ref:
        refs = [args.ref]
    else:
        raise SystemExit("donner une ref ou --day AAAA-MM-JJ")

    os.makedirs(FICHES, exist_ok=True)
    for ref in refs:
        doc = collect(ref)
        out = os.path.join(FICHES, slugify(ref) + ".source.json")
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2)
        if not args.quiet:
            print(f"{ref}")
            print(f"  hebreu           : {len(doc['michna']['hebreu'])} car.")
            print(f"  anglais Davidson : {len(doc['michna']['anglais_davidson'])} car.")
            print(f"  anglais Kulp     : {len(doc['michna']['anglais_kulp'])} car.")
            print(f"  explication Kulp : {len(doc['explication_kulp'])} paragraphes")
            print(f"  Bartenura        : {doc['bartenura']['n_sections']} sections")
            print(f"  Talmud           : {', '.join(doc['talmud']['refs']) or 'aucun (pas de Guemara)'}")
            print(f"  -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
