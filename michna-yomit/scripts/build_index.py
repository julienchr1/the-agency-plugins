#!/usr/bin/env python3
"""Construit data/tractates.json : les 63 traites de la Michna dans l'ordre
canonique du Shas, avec le nombre de michnaiot par chapitre (source : API
/shape de Sefaria) et le titre exact du Bartenura correspondant.

Usage : python3 scripts/build_index.py [--refresh]
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402
import sefaria  # noqa: E402

OUT = paths.data("tractates.json")

# Ordre canonique du Shas. (titre Sefaria, nom francais usuel, translitteration
# utilisee par dafyomi.co.il pour le calendrier Mishnah Yomis)
SEDARIM = [
    ("Zeraim", "Zeraïm", [
        ("Mishnah Berakhot", "Berakhot"), ("Mishnah Peah", "Péa"),
        ("Mishnah Demai", "Demaï"), ("Mishnah Kilayim", "Kilayim"),
        ("Mishnah Sheviit", "Chevi'it"), ("Mishnah Terumot", "Teroumot"),
        ("Mishnah Maasrot", "Maasrot"), ("Mishnah Maaser Sheni", "Maaser Cheni"),
        ("Mishnah Challah", "'Halla"), ("Mishnah Orlah", "Orla"),
        ("Mishnah Bikkurim", "Bikourim"),
    ]),
    ("Moed", "Moëd", [
        ("Mishnah Shabbat", "Chabbat"), ("Mishnah Eruvin", "Erouvin"),
        ("Mishnah Pesachim", "Pessa'him"), ("Mishnah Shekalim", "Chekalim"),
        ("Mishnah Yoma", "Yoma"), ("Mishnah Sukkah", "Souka"),
        ("Mishnah Beitzah", "Beitsa"), ("Mishnah Rosh Hashanah", "Roch Hachana"),
        ("Mishnah Ta'anit", "Taanit"), ("Mishnah Megillah", "Meguila"),
        ("Mishnah Moed Katan", "Moëd Katan"), ("Mishnah Chagigah", "'Haguiga"),
    ]),
    ("Nashim", "Nachim", [
        ("Mishnah Yevamot", "Yevamot"), ("Mishnah Ketubot", "Ketoubot"),
        ("Mishnah Nedarim", "Nedarim"), ("Mishnah Nazir", "Nazir"),
        ("Mishnah Sotah", "Sota"), ("Mishnah Gittin", "Guitin"),
        ("Mishnah Kiddushin", "Kidouchin"),
    ]),
    ("Nezikin", "Nezikin", [
        ("Mishnah Bava Kamma", "Baba Kama"), ("Mishnah Bava Metzia", "Baba Metsia"),
        ("Mishnah Bava Batra", "Baba Batra"), ("Mishnah Sanhedrin", "Sanhedrin"),
        ("Mishnah Makkot", "Makot"), ("Mishnah Shevuot", "Chevouot"),
        ("Mishnah Eduyot", "Edouyot"), ("Mishnah Avodah Zarah", "Avoda Zara"),
        ("Pirkei Avot", "Pirkei Avot"), ("Mishnah Horayot", "Horayot"),
    ]),
    ("Kodashim", "Kodachim", [
        ("Mishnah Zevachim", "Zeva'him"), ("Mishnah Menachot", "Mena'hot"),
        ("Mishnah Chullin", "'Houlin"), ("Mishnah Bekhorot", "Bekhorot"),
        ("Mishnah Arakhin", "Arakhin"), ("Mishnah Temurah", "Temoura"),
        ("Mishnah Keritot", "Keritot"), ("Mishnah Meilah", "Meïla"),
        ("Mishnah Tamid", "Tamid"), ("Mishnah Middot", "Midot"),
        ("Mishnah Kinnim", "Kinim"),
    ]),
    ("Tahorot", "Taharot", [
        ("Mishnah Kelim", "Kelim"), ("Mishnah Oholot", "Ohalot"),
        ("Mishnah Negaim", "Negaïm"), ("Mishnah Parah", "Para"),
        ("Mishnah Tahorot", "Taharot"), ("Mishnah Mikvaot", "Mikvaot"),
        ("Mishnah Niddah", "Nida"), ("Mishnah Makhshirin", "Makhchirin"),
        ("Mishnah Zavim", "Zavim"), ("Mishnah Tevul Yom", "Tevoul Yom"),
        ("Mishnah Yadayim", "Yadayim"), ("Mishnah Oktzin", "Oktsin"),
    ]),
]

# Le titre du Bartenura n'est pas toujours "Bartenura on <titre>".
BARTENURA_OVERRIDES = {"Mishnah Ta'anit": "Bartenura on Mishnah Taanit"}


def bartenura_title(title: str) -> str | None:
    candidates = [BARTENURA_OVERRIDES.get(title), f"Bartenura on {title}"]
    for cand in [c for c in candidates if c]:
        try:
            data = sefaria.shape(cand)
        except Exception:
            continue
        if isinstance(data, list) and data and "chapters" in data[0]:
            return cand
    return None


def main() -> None:
    tractates = []
    for seder_key, seder_fr, books in SEDARIM:
        for title, name_fr in books:
            shp = sefaria.shape(title)
            if not (isinstance(shp, list) and shp and "chapters" in shp[0]):
                raise SystemExit(f"/shape a echoue pour {title}: {shp!r}")
            node = shp[0]
            chapters = node["chapters"]
            if not all(isinstance(c, int) for c in chapters):
                raise SystemExit(f"structure inattendue pour {title}: {chapters!r}")
            bart = bartenura_title(title)
            tractates.append({
                "title": title,
                "he_title": node.get("heTitle"),
                "name_fr": name_fr,
                "seder": seder_key,
                "seder_fr": seder_fr,
                "chapters": chapters,
                "n_chapters": len(chapters),
                "n_mishnayot": sum(chapters),
                "bartenura_title": bart,
            })
            print(f"  {title:28s} {len(chapters):3d} ch. {sum(chapters):5d} mich."
                  f"  bartenura={'oui' if bart else 'NON'}", flush=True)

    payload = {
        "source": "https://www.sefaria.org/api/shape/<traite>",
        "generated_by": "scripts/build_index.py",
        "n_tractates": len(tractates),
        "n_mishnayot_total": sum(t["n_mishnayot"] for t in tractates),
        "tractates": tractates,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"\n{len(tractates)} traites, {payload['n_mishnayot_total']} michnaiot -> {OUT}")


if __name__ == "__main__":
    main()
