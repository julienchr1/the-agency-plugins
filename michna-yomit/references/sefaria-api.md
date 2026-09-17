# API Sefaria — endpoints utilisés

Tous vérifiés le 17 septembre 2026. Base : `https://www.sefaria.org/api`.
Aucune clé requise. Le client `scripts/sefaria.py` met en cache dans
`data/cache/`.

## Structure d'un traité

```
GET /shape/Mishnah%20Zevachim
```

→ `[{"title":…, "heTitle":…, "section":"Seder Kodashim",
     "length": 14, "chapters": [4,5,6,…]}]`

`chapters` = nombre de michnaiot par chapitre. C'est la base du calendrier.

Pour le Bartenura, `chapters` est une liste **de listes** : le nombre de
sections de commentaire par michna.

```
GET /shape/Bartenura%20on%20Mishnah%20Zevachim
```

## Texte d'une michna

L'API **v2** est celle à utiliser : elle renvoie hébreu et anglais déjà
segmentés dans un seul appel.

```
GET /texts/Mishnah_Oholot.2.4?context=0&commentary=0
```

- `he` → hébreu (Torat Emet 357, domaine public)
- `text` → anglais (William Davidson Edition par défaut)

Pour choisir une version : `&ven=Mishnah%20Yomit%20by%20Dr.%20Joshua%20Kulp`.

Versions disponibles pour une référence :

```
GET /v3/texts/Mishnah%20Oholot%202:4?version=all
```

**Il n'existe pratiquement pas de traduction française de la Michna sur
Sefaria** (seul Berakhot en a une, plus le Talmud de Jérusalem de Moïse
Schwab). Le français du plugin est donc rédigé d'après l'hébreu, avec
l'anglais en appui — et ne doit jamais être présenté comme une source
Sefaria.

## Bartenura

```
GET /texts/Bartenura_on_Mishnah_Oholot.2.4?context=0&commentary=0
```

- `he` → liste de segments ; chaque segment est `<b>lemme</b> commentaire`
- `text` → liste alignée, en anglais, sous la forme
  `lemme hébreu (glose) - commentaire`

Le titre est `Bartenura on <titre du traité>`, avec deux exceptions :
- `Mishnah Ta'anit` → `Bartenura on Mishnah Taanit` (sans apostrophe)
- `Pirkei Avot` → `Bartenura on Pirkei Avot`

Le Bartenura existe pour les **63 traités** (vérifié).

## Explication anglaise suivie (Dr. Joshua Kulp)

```
GET /texts/English_Explanation_of_Mishnah_Oholot.2.4?context=0&commentary=0
```

→ `text` : liste de paragraphes, le premier souvent intitulé
`<b>Introduction</b>`. Couvre l'ensemble de la Michna. C'est le meilleur appui
pour rédiger l'explication française.

## Renvois

```
GET /links/Mishnah_Oholot.2.4?with_text=0
```

Filtrer `category == "Talmud"` et ne garder que les références de la forme
`Traité 12a` — le reste mêle Yerushalmi, commentaires et introductions.

## Titres des traités : pièges

Sefaria n'utilise pas toujours l'orthographe attendue :

| attendu | Sefaria |
|---|---|
| Keilim | `Mishnah Kelim` |
| Uktzin | `Mishnah Oktzin` |
| Ohalot | `Mishnah Oholot` |
| Avot | `Pirkei Avot` (sans « Mishnah ») |
| Taanit | `Mishnah Ta'anit` (avec apostrophe) |

La liste canonique des 63 titres est figée dans `scripts/build_index.py` et le
résultat dans `data/tractates.json`.
