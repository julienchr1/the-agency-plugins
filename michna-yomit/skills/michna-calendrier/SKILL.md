---
name: michna-calendrier
description: Tient et interroge le calendrier du programme Michna Yomit — où en est-on, quelle michna à telle date, avancement par traité et par seder, date de fin prévue, recalage du calendrier sur la réalité. Déclencher sur « où en est-on », « avancement », « quelle michna le 12 octobre », « quand finit-on Ohalot », « combien reste-t-il », « le calendrier est décalé », « recale le programme ».
---

# Calendrier du programme

Le calendrier est un fichier généré, `data/calendar.json` : une entrée par
jour, avec la date, les références du jour, le libellé et la position. Il est
reconstruit à partir de trois éléments :

- `data/tractates.json` — les 63 traités et le nombre de michnaiot par
  chapitre, tirés de l'API `/shape` de Sefaria ;
- `data/program.json` — la définition du programme (départ, rythme, règle de
  saut, calibration) ;
- l'ordre canonique du Shas, en bouclant depuis le traité de départ.

## Interroger

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py today
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py date 2026-10-12
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py progress
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py find "Mishnah Oholot 3:1"
```

`progress` donne les michnaiot faites sur 4192, les jours écoulés, le restant,
la date de fin prévue, et l'avancement traité par traité dans l'ordre du cycle.

Pour répondre à « où en est-on », lancer `progress` et **résumer** : position
du jour, part du cycle accomplie, traité en cours et ce qu'il reste dedans,
prochain jalon. Ne pas recopier la sortie brute.

## Le point délicat : le découpage des michnaiot

Les éditions ne découpent pas les michnaiot de façon identique. Entre
Zeva'him 1:1 et Ohalot 2, Sefaria en compte **une de plus** que l'édition
suivie par dafyomi.co.il. Le calendrier gère cela avec
`offset_mishnayot` dans `program.json` — actuellement `-1`, calibré sur une
observation réelle.

Le bloc `calibration` de `program.json` conserve cette observation, et chaque
`build` vérifie qu'elle est toujours satisfaite. Si `build` affiche `ECART`,
ne pas ignorer : recalibrer.

## Recaler le calendrier

Quand l'utilisateur dit que le calendrier ne correspond pas à ce qu'il étudie,
demander **une** information précise : à telle date, quelle est la *première*
des deux michnaiot. Puis :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py calibrate 2026-09-17 "Mishnah Oholot 2:4"
```

Cela recalcule `offset_mishnayot`, l'écrit dans `program.json` et régénère le
calendrier. Annoncer l'offset trouvé et ce qui change pour aujourd'hui.

Pour un changement de rythme ou de règle de saut, modifier `program.json`
(`per_day`, `skip` parmi `none` / `shabbat` / `shabbat+yomtov`) puis
`calendar_build.py build`. Prévenir que cela déplace toutes les dates futures.

## Source de référence externe

Le programme est aligné, à une michna près, sur le **16ᵉ cycle Mishnah Yomi**
du Dafyomi Advancement Forum :
<https://www.dafyomi.co.il/calendars/myomi/todays_mishnah.php>

En cas de doute sur la position réelle, cette page est la référence à
consulter — elle affiche la semaine en cours. C'est elle qui a servi à la
calibration. Y revenir si un écart est soupçonné, et recalibrer si besoin.

## Régénérer l'index des traités

Seulement si l'on soupçonne un problème de comptage :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/build_index.py     # réinterroge /shape pour les 63 traités
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py build
```
