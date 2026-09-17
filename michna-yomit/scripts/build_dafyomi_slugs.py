#!/usr/bin/env python3
"""Construit data/dafyomi_slugs.json : correspondance traite du Talmud Bavli
-> slug et prefixe utilises par dafyomi.co.il, chaque entree etant VERIFIEE
par une requete HTTP sur une page 'background' reelle.

  python3 scripts/build_dafyomi_slugs.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

OUT = paths.data("dafyomi_slugs.json")

# (nom Sefaria, dernier daf, candidats slug, candidats prefixe)
CANDIDATES = [
    ("Berakhot", 64, ["berachos", "brachos"], ["br", "bk"]),
    ("Shabbat", 157, ["shabbos", "shabos"], ["sb", "sh"]),
    ("Eruvin", 105, ["eruvin", "eiruvin"], ["ev", "er"]),
    ("Pesachim", 121, ["pesachim", "psachim"], ["ps", "pe"]),
    ("Shekalim", 22, ["shekalim"], ["sk", "sh"]),
    ("Yoma", 88, ["yoma"], ["ym", "yo"]),
    ("Sukkah", 56, ["sukah", "sukkah"], ["su", "sk"]),
    ("Beitzah", 40, ["beitzah", "beitza"], ["bz", "bt"]),
    ("Rosh Hashanah", 35, ["rhashanah", "roshhashanah"], ["rh"]),
    ("Taanit", 31, ["taanis", "taanit"], ["tn", "ta"]),
    ("Megillah", 32, ["megilah", "megillah"], ["mg", "me"]),
    ("Moed Katan", 29, ["mkatan", "moedkatan"], ["mo", "mk"]),
    ("Chagigah", 27, ["chagigah", "chagiga"], ["cg", "ch"]),
    ("Yevamot", 122, ["yevamos", "yevamot"], ["ye", "yv"]),
    ("Ketubot", 112, ["kesuvos", "ketubos"], ["kv", "ks"]),
    ("Nedarim", 91, ["nedarim"], ["nd", "ne"]),
    ("Nazir", 66, ["nazir"], ["nz", "nr"]),
    ("Sotah", 49, ["sotah", "sota"], ["so", "st"]),
    ("Gittin", 90, ["gitin", "gittin"], ["gt", "gi"]),
    ("Kiddushin", 82, ["kidushin", "kiddushin"], ["kd", "ki"]),
    ("Bava Kamma", 119, ["bkama", "bavakama"], ["bk"]),
    ("Bava Metzia", 119, ["bmetzia", "bavametzia"], ["bm"]),
    ("Bava Batra", 176, ["bbasra", "bavabasra"], ["bb"]),
    ("Sanhedrin", 113, ["sanhedrin"], ["sn", "sa"]),
    ("Makkot", 24, ["makos", "makkos"], ["mk", "ma"]),
    ("Shevuot", 49, ["shevuos", "shvuos"], ["sv", "sh"]),
    ("Avodah Zarah", 76, ["avodahzarah", "azarah"], ["az"]),
    ("Horayot", 14, ["horayos", "horios"], ["hr", "ho"]),
    ("Zevachim", 120, ["zevachim"], ["zv", "ze"]),
    ("Menachot", 110, ["menachos", "menachot"], ["mn", "me"]),
    ("Chullin", 142, ["chulin", "chullin"], ["ch"]),
    ("Bekhorot", 61, ["bechoros", "bchoros"], ["be", "bc"]),
    ("Arakhin", 34, ["erchin", "arachin"], ["er", "ar"]),
    ("Temurah", 34, ["temurah", "temura"], ["tm", "te"]),
    ("Keritot", 28, ["kerisus", "krisus"], ["kr", "ke"]),
    ("Meilah", 22, ["meilah", "meila"], ["ml", "me"]),
    ("Niddah", 73, ["nidah", "niddah"], ["nd", "ni"]),
]

UA = "michna-yomit-plugin/1.0"


def exists(url: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA}, method="HEAD")
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except urllib.error.HTTPError:
        return False
    except Exception:
        return False


def main() -> None:
    found, missing = {}, []
    for name, last, slugs, prefixes in CANDIDATES:
        hit = None
        for daf in (3, 5, last - 1):
            for slug in slugs:
                for pref in prefixes:
                    url = (f"https://www.dafyomi.co.il/{slug}/backgrnd/"
                           f"{pref}-in-{daf:03d}.htm")
                    if exists(url):
                        hit = {"slug": slug, "prefix": pref, "last_daf": last,
                               "verified_url": url}
                        break
                if hit:
                    break
            if hit:
                break
        if hit:
            found[name] = hit
            print(f"  OK   {name:16s} {hit['slug']}/{hit['prefix']}")
        else:
            missing.append(name)
            print(f"  ---  {name:16s} introuvable")

    payload = {
        "source": "https://www.dafyomi.co.il/ (Kollel Iyun Hadaf)",
        "url_pattern": "https://www.dafyomi.co.il/{slug}/backgrnd/{prefix}-in-{daf:03d}.htm",
        "generated_by": "scripts/build_dafyomi_slugs.py",
        "note": "Chaque entree a ete verifiee par une requete HTTP 200.",
        "not_found": missing,
        "sans_pages_background": {"Tamid": "dafyomi.co.il ne publie pas de pages background pour Tamid (verifie le 2026-09-17)."},
        "tractates": found,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"\n{len(found)} traites verifies, {len(missing)} manquants -> {OUT}")


if __name__ == "__main__":
    main()
