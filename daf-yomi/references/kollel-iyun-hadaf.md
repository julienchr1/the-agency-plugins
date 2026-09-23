# dafyomi.co.il — background et insights

Le Kollel Iyun Hadaf publie deux pages par daf, qui ne font pas la même chose.
Schéma d'URL vérifié pour 37 traités (`data/dafyomi_slugs.json`) :

```
https://www.dafyomi.co.il/{slug}/backgrnd/{prefix}-in-{daf sur 3 chiffres}.htm
https://www.dafyomi.co.il/{slug}/insites/{prefix}-dt-{daf sur 3 chiffres}.htm
```

**Tamid n'a pas de pages background.**

## Background — un glossaire indexé par ligne

Contient, dans l'ordre :

1. le nombre de lignes de chaque amoud (`5a - 50 lines; 5b - 56 lines`) ;
2. une **section GIRSA** : corrections textuelles des A'haronim, d'après le
   Bach et les notes marginales du Vilna Shas — que Sefaria ne porte pas ;
3. des entrées numérotées **keyées sur le numéro de ligne** du daf :

```
[ligne 27] קוביוסטוס KOVYUSTUS - a gambler (TOSFOS); kidnapper (RASHI)
[ligne 30] מנה של קודש כפול היה - the Maneh used for the Mishkan was double
```

C'est le matériau du champ `glossaire` de la fiche. Comme il est indexé par
ligne, il s'accroche naturellement au texte.

## Insights — les difficultés et leurs résolutions

Items numérotés, en QUESTION / ANSWERS, avec les sources nommées :

```
1) WAS MOSHE A THIEF OR A 'KUVYUSTUS'?
QUESTION: … TOSFOS cites RASHI in Chulin 91b who explains …
ANSWERS: (a) TOSFOS in Bava Basra 92b justifies … (b) The SHITAH MEKUBETZES …
```

C'est le matériau du champ `difficulte`. Volume très variable : de 3 400
caractères (Bekhorot 5) à 22 700 (Meguila 13).

## Ce qu'ils apportent réellement

Les insights ne comblent pas les lacunes de Sefaria — Rashi et Tossafot y sont,
par l'API `links`. Ce qu'ils apportent, ce sont les **résolutions des
A'haronim** (Chitta Mekoubetset, Tzela'h, Maharcha…) que Sefaria n'indexe pas,
et les **variantes textuelles**.

## Précautions

Site tiers : le parseur met en cache, et il ne faut pas le marteler. Les corps
d'insights sont conservés entiers jusqu'à 6 000 caractères ; au-delà, l'item
porte `tronque: true` et il faut consulter l'URL.
