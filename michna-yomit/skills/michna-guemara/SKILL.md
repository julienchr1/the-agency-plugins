---
name: michna-guemara
description: Compile les sujets de Guemara qui portent sur une michna donnée — folios du Talmud liés, notions de fond depuis les pages « background » de dafyomi.co.il, et la sugya en jeu. Déclencher sur « les sujets de guemara sur cette michna », « quelle guemara sur Zeva'him 3:1 », « le daf correspondant », « background dafyomi », « approfondis cette michna », « compile la guemara ».
---

# Sujets de Guemara sur une michna

Sert à approfondir une michna au-delà du Bartenura, en restant sourcé.

## 1. Les renvois

Le `.source.json` produit par `michna-fiche` contient déjà
`talmud.refs` (les folios du Bavli liés à cette michna, via l'API `/links` de
Sefaria) et `talmud.dafyomi` (les URL correspondantes sur dafyomi.co.il).

S'il n'existe pas encore :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/fetch_mishna.py "Mishnah Zevachim 3:1"
```

Beaucoup de traités de Kodashim et de Taharot n'ont **pas** de Guemara
babylonienne. Dans ce cas `talmud.refs` est vide ou ne contient que des
renvois depuis d'autres traités — c'est normal et il faut le dire, pas le
combler. Les renvois croisés (une michna d'Oktsin discutée dans Pessa'him)
sont eux-mêmes intéressants : les signaler comme tels.

## 2. Le texte de la Guemara

Lire le folio sur Sefaria :

```
https://www.sefaria.org/api/texts/Zevachim_10a?context=0&commentary=0
```

`he` donne l'araméen, `text` la traduction anglaise du William Davidson
Talmud. Repérer la sugya qui discute effectivement notre michna — pas tout le
folio.

## 3. Les notions de fond (dafyomi.co.il)

Le schéma d'URL, vérifié :

```
https://www.dafyomi.co.il/{slug}/backgrnd/{prefix}-in-{daf sur 3 chiffres}.htm
```

La table `data/dafyomi_slugs.json` donne `slug` et `prefix` pour les
**37 traités** du Bavli, chaque entrée vérifiée par requête HTTP. Exemple :
Chullin 140 → `chulin/backgrnd/ch-in-140.htm`.

Les pages « insights » (`/insites/{prefix}-dt-{daf}.htm`) donnent les analyses
plutôt que les définitions.

Récupérer la page avec WebFetch. Ces pages sont une source externe : en
extraire les définitions utiles, en citant le folio, sans recopier de longs
passages. Elles n'ont pas de pages « background » pour **Tamid**.

## 4. La compilation

Produire, en français :

- **La sugya** : quelle question la Guemara pose sur cette michna, comment
  elle la résout. Une section par folio significatif.
- **Notions de fond** : les termes et realia expliqués par les pages
  background, chacun en une à trois phrases.
- **Ce que cela change pour la michna** : en quoi la Guemara éclaire, restreint
  ou déplace la lecture simple — et ce que le Bartenura en a retenu.
- **Sources** : chaque folio avec son lien Sefaria, chaque page dafyomi.co.il
  avec son URL.

Écrire dans `fiches/<slug>.guemara.md`. Cette compilation est un complément :
elle ne remplace pas la fiche et ne modifie pas le `.fr.json`.

## Limite à tenir

Ne jamais présenter comme « la Guemara dit » un contenu qui n'a pas été lu sur
Sefaria dans cette session. Si un folio est inaccessible, le dire.
