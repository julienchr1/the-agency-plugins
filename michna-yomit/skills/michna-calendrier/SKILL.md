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

## La source de vérité, c'est l'utilisateur

**Le calendrier se calibre sur ce que l'utilisateur étudie réellement, jamais
sur un calendrier externe.** C'est la règle la plus importante de cette skill.

`data/program.json` porte un `offset_mishnayot` (actuellement `0`) et un bloc
`calibration` qui conserve une observation datée. Chaque `build` revérifie que
cette observation est toujours satisfaite, et affiche `ECART` sinon.

Ce programme **n'est pas** le cycle « Mishnah Yomi » de dafyomi.co.il. Les deux
ont une michna d'écart : le 17/09/2026, ce programme était à Ohalot 2:5-6 quand
le cycle officiel était à Ohalot 2:4-5. Ne jamais « corriger » le calendrier
pour le faire coller au site officiel — c'est l'erreur qui a déjà été commise,
et elle décale tout d'une michna.

Si l'utilisateur signale un écart, sa position est juste par définition :
recalibrer immédiatement, sans chercher à arbitrer avec une source externe.

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

## Un repère externe, à ne pas confondre avec la référence

Le Dafyomi Advancement Forum publie son propre cycle « Mishnah Yomi », à
2 michnaiot par jour :
<https://www.dafyomi.co.il/calendars/myomi/todays_mishnah.php>

Il est proche de ce programme mais **décalé d'une michna**. C'est un point de
comparaison utile pour comprendre un écart, **jamais** une raison de recaler le
calendrier. Seule la position réelle de l'utilisateur fait foi.

## Régénérer l'index des traités

Seulement si l'on soupçonne un problème de comptage :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/build_index.py     # réinterroge /shape pour les 63 traités
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py build
```
