"""Lecture des pages du Kollel Iyun Hadaf (dafyomi.co.il).

Deux pages par daf, qui ne font pas la meme chose :

- `background` : un glossaire **indexe par numero de ligne** du daf (termes,
  realia, versets), precede d'une section GIRSA de variantes textuelles.
- `insights`   : des difficultes numerotees en QUESTION / ANSWERS, avec les
  sources nommees. Elles discutent souvent un Rashi ou un Tossafot que Sefaria
  ne porte pas — la source externe comble alors une lacune reelle.

Schema d'URL verifie :
  https://www.dafyomi.co.il/{slug}/backgrnd/{prefix}-in-{daf:03d}.htm
  https://www.dafyomi.co.il/{slug}/insites/{prefix}-dt-{daf:03d}.htm
"""
from __future__ import annotations

import html as H
import os
import re
import time
import urllib.error
import urllib.request

UA = "daf-yomi-plugin/1.0"


def _fetch(url: str, cache_dir: str, retries: int = 2) -> str | None:
    os.makedirs(cache_dir, exist_ok=True)
    cp = os.path.join(cache_dir, urllib.parse.quote(url, safe="") + ".html")
    if os.path.exists(cp):
        with open(cp, encoding="utf-8") as fh:
            return fh.read()
    raw = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1.5 * (attempt + 1))
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    if raw is None:
        return None
    for enc in ("utf-8", "windows-1255", "cp1252", "latin-1"):
        try:
            txt = raw.decode(enc)
            break
        except Exception:
            continue
    else:
        return None
    with open(cp, "w", encoding="utf-8") as fh:
        fh.write(txt)
    return txt


import urllib.parse  # noqa: E402  (apres _fetch pour rester lisible)


def _texte(h: str) -> str:
    h = re.sub(r"<(script|style).*?</\1>", "", h, flags=re.S | re.I)
    h = re.sub(r"<br\s*/?>|</p>|</div>|</tr>|</h\d>", "\n", h, flags=re.I)
    t = H.unescape(re.sub(r"<[^>]+>", " ", h))
    t = re.sub(r"[ \t\xa0]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


KINDS = {"background": ("backgrnd", "in"),
         "insights": ("insites", "dt"),
         "points": ("points", "ps")}


def url_page(slug: str, prefix: str, daf: int, kind: str) -> str:
    seg, pref = KINDS[kind]
    return (f"https://www.dafyomi.co.il/{slug}/{seg}/"
            f"{prefix}-{pref}-{daf:03d}.htm")


HEB = re.compile(r"[\u0590-\u05FF]")
ETAPE = re.compile(r"^\(?([a-z])\)\s*(.+)$")
SOUS = re.compile(r"^(\d+)\.\s*(.+)$")
SUJET = re.compile(r"^(\d+)\)\s+([A-Z].*)$")


def points(slug: str, prefix: str, daf: int, cache_dir: str) -> dict:
    """Le « point by point outline » : le squelette dialectique du daf.

    Chaque etape y est precedee de son LEMME ARAMEEN, puis glosee avec son
    role logique — Question, Answer, Beraisa, le nom d'un Amora. C'est une
    trame que ni `background` (glossaire) ni `insights` (difficultes) ne
    donnent : elle dit *comment l'argument avance*.

    Structure : sujets numerotes `N) TITRE`, etapes `(a)`, sous-etapes `1.`.
    Le lemme est la ligne hebraique qui PRECEDE la glose.
    """
    u = url_page(slug, prefix, daf, "points")
    h = _fetch(u, cache_dir)
    if not h:
        return {"url": u, "disponible": False, "sujets": []}
    t = _texte(h)
    lignes = [l.strip() for l in t.splitlines() if l.strip()]
    sujets, courant, lemme, parent = [], None, "", ""
    for l in lignes:
        m = SUJET.match(l)
        if m and len(l) < 110:
            courant = {"n": int(m.group(1)), "titre": m.group(2).strip(),
                       "etapes": []}
            sujets.append(courant)
            lemme, parent = "", ""
            continue
        if courant is None:
            continue
        if HEB.search(l):
            lemme = l
            continue
        me, ms = ETAPE.match(l), SOUS.match(l)
        if me or ms:
            texte = (me or ms).group(2).strip()
            role = ""
            # Le role peut porter une precision entre parentheses :
            # "Answer (R. Yochanan ben Zakai): ..." ou "Version #3 - Rav Mordechai: ..."
            r = re.match(r"^([A-Z][^:]{0,60}?)\s*:\s*(.+)$", texte)
            if r:
                role, texte = r.group(1).strip(), r.group(2).strip()
            rep = (me or ms).group(1)
            if me:
                parent = rep
                ident = f"{courant['n']}.{rep}"
            else:
                ident = f"{courant['n']}.{parent}.{rep}" if parent \
                    else f"{courant['n']}.{rep}"
            # `id` est la cle stable que le francais reference : elle permet
            # d'ecrire une etape sans jamais saisir son lemme arameen.
            courant["etapes"].append({
                "id": ident,
                "repere": rep,
                "niveau": 1 if me else 2,
                "lemme": lemme,
                "role": role,
                "texte": texte,
            })
            lemme = ""
    return {"url": u, "disponible": True, "sujets": sujets}


def background(slug: str, prefix: str, daf: int, cache_dir: str) -> dict:
    """Glossaire indexe par ligne + variantes textuelles."""
    u = url_page(slug, prefix, daf, "background")
    h = _fetch(u, cache_dir)
    if not h:
        return {"url": u, "disponible": False, "entrees": [], "girsa": []}
    t = _texte(h)
    lignes_daf = re.search(r"\[(\d+a\s*-\s*\d+\s*lines?;\s*\d+b\s*-\s*\d+\s*lines?)\]", t)
    # section GIRSA : entre le marqueur et la ligne d'asterisques de fin
    girsa = []
    g = re.search(r"GIRSA SECTION\*+(.*?)\*{10,}", t, re.S)
    if g:
        for m in re.finditer(r"\[\d+\]\s*(.+?)(?=\n\[\d+\]|\Z)", g.group(1), re.S):
            girsa.append(re.sub(r"\s+", " ", m.group(1)).strip())
    # entrees numerotees : "1 ) [line 3] <hebreu> TRANSLIT - sens"
    entrees = []
    for m in re.finditer(r"\n\s*(\d+)\s*\)\s*(.+?)(?=\n\s*\d+\s*\)|\Z)", t, re.S):
        bloc = re.sub(r"\s+", " ", m.group(2)).strip()
        ligne = re.match(r"\[line (\d+)\]\s*(.*)", bloc)
        entrees.append({
            "n": int(m.group(1)),
            "ligne": int(ligne.group(1)) if ligne else None,
            "texte": (ligne.group(2) if ligne else bloc)[:600],
        })
    return {"url": u, "disponible": True,
            "lignes_daf": lignes_daf.group(1) if lignes_daf else None,
            "girsa": girsa, "entrees": entrees}


def insights(slug: str, prefix: str, daf: int, cache_dir: str) -> dict:
    """Difficultes numerotees. Chaque item commence par "N)" suivi du titre
    sur la MEME ligne, puis le corps, avec ou sans etiquette QUESTION/ANSWERS.

    On decoupe par positions des marqueurs plutot que par une seule expression
    a lookahead : les corps contiennent eux-memes des "(a)", "(b)", "1)" qui
    font echouer toute approche globale.
    """
    u = url_page(slug, prefix, daf, "insights")
    h = _fetch(u, cache_dir)
    if not h:
        return {"url": u, "disponible": False, "items": []}
    t = _texte(h)
    bornes = [(m.start(), int(m.group(1)))
              for m in re.finditer(r"\n\s*(\d+)\s*\)\s*\"?[A-Z]", t)]
    items = []
    for i, (pos, n) in enumerate(bornes):
        fin = bornes[i + 1][0] if i + 1 < len(bornes) else len(t)
        bloc = t[pos:fin].strip()
        # premiere ligne = titre
        lignes = [l.strip() for l in bloc.splitlines() if l.strip()]
        titre = re.sub(r"^\d+\s*\)\s*", "", lignes[0]).strip().strip('"')
        corps = re.sub(r"\s+", " ", " ".join(lignes[1:])).strip()
        q = re.search(r"QUESTIONS?:(.*?)(?=ANSWERS?:|\Z)", corps, re.S | re.I)
        a_ = re.search(r"ANSWERS?:(.*)", corps, re.S | re.I)
        # Toutes les pages n'etiquettent pas QUESTION/ANSWERS : on conserve
        # systematiquement le corps entier, pour ne rien perdre en silence.
        items.append({
            "n": n,
            "titre": titre,
            "question": (q.group(1).strip() if q else "")[:2500],
            "reponses": (a_.group(1).strip() if a_ else "")[:4000],
            "corps": corps[:6000],
            "tronque": len(corps) > 6000,
        })
    return {"url": u, "disponible": True, "items": items}
