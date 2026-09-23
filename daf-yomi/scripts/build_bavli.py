#!/usr/bin/env python3
"""Construit data/bavli.json : les 37 traites du Talmud de Babylone du cycle
Daf Yomi, avec leur plage de dafim et le slug dafyomi.co.il correspondant.

  python3 scripts/build_bavli.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402
import sefaria  # noqa: E402

# Ordre du cycle Daf Yomi. (titre Sefaria, nom francais, seder)
TRAITES = [
    ("Berakhot", "Berakhot", "Zeraïm"),
    ("Shabbat", "Chabbat", "Moëd"),
    ("Eruvin", "Erouvin", "Moëd"),
    ("Pesachim", "Pessa'him", "Moëd"),
    ("Shekalim", "Chekalim", "Moëd"),   # Yerushalmi dans le cycle Daf Yomi
    ("Yoma", "Yoma", "Moëd"),
    ("Sukkah", "Souka", "Moëd"),
    ("Beitzah", "Beitsa", "Moëd"),
    ("Rosh Hashanah", "Roch Hachana", "Moëd"),
    ("Taanit", "Taanit", "Moëd"),
    ("Megillah", "Meguila", "Moëd"),
    ("Moed Katan", "Moëd Katan", "Moëd"),
    ("Chagigah", "'Haguiga", "Moëd"),
    ("Yevamot", "Yevamot", "Nachim"),
    ("Ketubot", "Ketoubot", "Nachim"),
    ("Nedarim", "Nedarim", "Nachim"),
    ("Nazir", "Nazir", "Nachim"),
    ("Sotah", "Sota", "Nachim"),
    ("Gittin", "Guitin", "Nachim"),
    ("Kiddushin", "Kidouchin", "Nachim"),
    ("Bava Kamma", "Baba Kama", "Nezikin"),
    ("Bava Metzia", "Baba Metsia", "Nezikin"),
    ("Bava Batra", "Baba Batra", "Nezikin"),
    ("Sanhedrin", "Sanhedrin", "Nezikin"),
    ("Makkot", "Makot", "Nezikin"),
    ("Shevuot", "Chevouot", "Nezikin"),
    ("Avodah Zarah", "Avoda Zara", "Nezikin"),
    ("Horayot", "Horayot", "Nezikin"),
    ("Zevachim", "Zeva'him", "Kodachim"),
    ("Menachot", "Mena'hot", "Kodachim"),
    ("Chullin", "'Houlin", "Kodachim"),
    ("Bekhorot", "Bekhorot", "Kodachim"),
    ("Arakhin", "Arakhin", "Kodachim"),
    ("Temurah", "Temoura", "Kodachim"),
    ("Keritot", "Keritot", "Kodachim"),
    ("Meilah", "Meïla", "Kodachim"),
    ("Tamid", "Tamid", "Kodachim"),
    ("Niddah", "Nida", "Taharot"),
]


def main() -> None:
    paths.ensure()
    slugs = json.load(open(os.path.join(paths.PLUGIN_DATA, "dafyomi_slugs.json"),
                           encoding="utf-8"))["tractates"]
    out = []
    for titre, fr, seder in TRAITES:
        # Chekalim est etudie dans le Yerushalmi par le cycle Daf Yomi : sa
        # reference Sefaria n'est pas la meme que celle des traites du Bavli.
        ref_base = "Jerusalem Talmud Shekalim" if titre == "Shekalim" else titre
        shp = sefaria.get("shape/" + ref_base.replace(" ", "%20"))
        node = shp[0] if isinstance(shp, list) and shp else {}
        n_amudim = node.get("length") or len(node.get("chapters") or [])
        # Sefaria indexe les amudim depuis 1a (folio 1, vide) : l'amoud
        # d'index i correspond au daf ceil(i/2). Le dernier daf est donc
        # ceil(longueur/2) — et non 1 + longueur//2.
        dernier = -(-n_amudim // 2)
        # Chekalim : le Yerushalmi est structure par chapitre sur Sefaria
        # (8 chapitres), alors que le cycle Daf Yomi en compte 22 dafim.
        # L'API calendrier fournit pour ces jours une PLAGE explicite du type
        # "Jerusalem Talmud Shekalim 4:2:15-3:3" : c'est elle qui fait foi.
        yerushalmi = titre == "Shekalim"
        if yerushalmi:
            dernier = 22
        s = slugs.get(titre)
        out.append({
            "titre": titre,
            "he_titre": node.get("heTitle"),
            "nom_fr": fr,
            "seder": seder,
            "ref_base": ref_base,
            "yerushalmi": yerushalmi,
            "ref_style": "plage" if yerushalmi else "amudim",
            "premier_daf": 2,
            "dernier_daf": dernier,
            "n_amudim": n_amudim,
            "dafyomi": {"slug": s["slug"], "prefix": s["prefix"]} if s else None,
            "background": bool(s) and titre != "Tamid",
        })
        print(f"  {titre:16s} 2a – {dernier}  ({n_amudim} amudim)"
              f"  dafyomi={'oui' if s else 'NON'}"
              f"{'  (pas de background)' if titre == 'Tamid' else ''}", flush=True)

    payload = {
        "source": "https://www.sefaria.org/api/shape/<traite>",
        "note": "Le Talmud commence en 2a : il n'y a pas de folio 1.",
        "n_traites": len(out),
        # Indicatif : la convention de comptage varie (le chiffre de 2711
        # souvent cite ne s'obtient pas par cette somme). Ce qui sert
        # reellement, c'est `dernier_daf` par traite — verifie traite par
        # traite contre les valeurs connues.
        "n_dafim_indicatif": sum(t["dernier_daf"] - 1 for t in out),
        "traites": out,
    }
    p = paths.data("bavli.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"\n{len(out)} traites, {payload['n_dafim_indicatif']} dafim (indicatif) -> {p}")


if __name__ == "__main__":
    main()
