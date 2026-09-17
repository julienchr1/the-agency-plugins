"""Client Sefaria minimal avec cache disque. Toutes les données textuelles du
plugin proviennent de cette couche : aucune source n'est inventee."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import sys

API = "https://www.sefaria.org/api"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

ROOT = paths.PLUGIN_ROOT
UA = "michna-yomit-plugin/1.0 (+https://www.sefaria.org)"


def _cache_path(key: str) -> str:
    safe = urllib.parse.quote(key, safe="")
    return os.path.join(paths.CACHE, safe + ".json")


def get(path: str, *, params: dict | None = None, cache: bool = True, retries: int = 3):
    """GET sur l'API Sefaria, avec cache disque et retries."""
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


def shape(title: str):
    return get("shape/" + urllib.parse.quote(title))


def text(ref: str, *, version: str | None = None):
    """Texte via l'API v2 : renvoie he + text (anglais) deja segmentes."""
    params = {"context": 0, "commentary": 0}
    if version:
        params["ven"] = version
    return get("texts/" + urllib.parse.quote(ref.replace(" ", "_")), params=params)


def versions(ref: str):
    return get("v3/texts/" + urllib.parse.quote(ref), params={"version": "all"})


def links(ref: str):
    return get("links/" + urllib.parse.quote(ref.replace(" ", "_")), params={"with_text": 0})


def sefaria_url(ref: str) -> str:
    return "https://www.sefaria.org/" + urllib.parse.quote(ref.replace(" ", "_").replace(":", "."))
