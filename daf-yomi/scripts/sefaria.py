"""Client Sefaria pour le Daf Yomi, avec cache disque.

Trois usages : le calendrier (quel daf a quelle date), le texte d'un amoud, et
les commentateurs attaches a un daf.

Point important : les commentateurs se recuperent par l'API `links`, PAS par la
reference directe `Rashi on <traite>.<daf>` qui ne renvoie que des fragments.
Mesure sur Berakhot 2a : 17 dibbourim / 1612 caracteres par `links`, contre
2 segments / 474 caracteres par la reference directe.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

API = "https://www.sefaria.org/api"
UA = "daf-yomi-plugin/1.0 (+https://www.sefaria.org)"


def _cache_path(key: str) -> str:
    return os.path.join(paths.CACHE, urllib.parse.quote(key, safe="") + ".json")


def get(path: str, *, params: dict | None = None, cache: bool = True,
        retries: int = 3):
    qs = "?" + urllib.parse.urlencode(params) if params else ""
    url = f"{API}/{path}{qs}"
    cp = _cache_path(path + qs)
    if cache and os.path.exists(cp):
        with open(cp, encoding="utf-8") as fh:
            return json.load(fh)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    else:
        raise RuntimeError(f"Sefaria injoignable pour {url}: {last}")
    if cache:
        os.makedirs(paths.CACHE, exist_ok=True)
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
    return data


# --------------------------------------------------------------- utilitaires
TAG = re.compile(r"<[^>]+>")
FOOTNOTE = re.compile(r"<i\s+data-commentator[^>]*>.*?</i>", re.S | re.I)
SUP = re.compile(r"<sup>.*?</sup>\s*<i\s+class=[\"']footnote[\"']>.*?</i>", re.S | re.I)


def clean(s) -> str:
    """Retire le balisage en preservant le texte."""
    import html as H
    if s is None:
        return ""
    if isinstance(s, list):
        return "\n".join(clean(x) for x in s)
    s = SUP.sub("", s)
    s = FOOTNOTE.sub("", s)
    s = s.replace("<br>", " ").replace("<br/>", " ")
    s = TAG.sub("", s)
    return re.sub(r"\s+", " ", H.unescape(s)).strip()


def flatten(x) -> list:
    if isinstance(x, list):
        out = []
        for i in x:
            out += flatten(i)
        return out
    return [x] if isinstance(x, str) else []


# ---------------------------------------------------------------- calendrier
def entree_calendrier(date_iso: str) -> dict | None:
    """L'entree Daf Yomi d'une date : libelle affiche ET reference exacte.

    Le champ `ref` fait foi : pour le Bavli il vaut "Bekhorot 5", mais pour
    Chekalim (etudie dans le Yerushalmi) c'est une plage du type
    "Jerusalem Talmud Shekalim 4:2:15-3:3".
    """
    y, m, d = date_iso.split("-")
    data = get("calendars", params={"year": int(y), "month": int(m), "day": int(d)})
    for item in data.get("calendar_items", []):
        if (item.get("title") or {}).get("en") == "Daf Yomi":
            return {"libelle": (item.get("displayValue") or {}).get("en"),
                    "ref": item.get("ref")}
    return None


def daf_du_jour(date_iso: str) -> str | None:
    """Le libelle du daf d'une date ISO. None hors cycle connu."""
    e = entree_calendrier(date_iso)
    return e["libelle"] if e else None


# --------------------------------------------------------------------- texte
def amoud(ref: str) -> dict:
    """Texte d'un amoud : araméen segmente + traduction anglaise d'appui."""
    d = get("texts/" + urllib.parse.quote(ref.replace(" ", "_")),
            params={"context": 0, "commentary": 0})
    if "error" in d:
        return {"error": d["error"], "he": [], "en": []}
    return {
        "he": [clean(s) for s in flatten(d.get("he")) if clean(s)],
        "en": [clean(s) for s in flatten(d.get("text")) if clean(s)],
    }


# ------------------------------------------------------------ commentateurs
def commentateurs(ref: str, noms: tuple[str, ...] = ("Rashi", "Tosafot")) -> dict:
    """Commentaires attaches a un amoud, via l'API links.

    Renvoie {nom: [{"ancre": ref du segment commente, "he": texte}, ...]}.
    """
    lk = get("links/" + urllib.parse.quote(ref.replace(" ", "_")),
             params={"with_text": 1})
    out: dict[str, list] = {n: [] for n in noms}
    for l in lk:
        nom = (l.get("collectiveTitle") or {}).get("en")
        if nom not in out:
            continue
        he = l.get("he") or ""
        if isinstance(he, list):
            he = " ".join(he)
        he = clean(he)
        if he:
            out[nom].append({"ancre": l.get("anchorRef") or l.get("ref"), "he": he})
    return out


def url(ref: str) -> str:
    return "https://www.sefaria.org/" + urllib.parse.quote(
        ref.replace(" ", "_").replace(":", "."))
