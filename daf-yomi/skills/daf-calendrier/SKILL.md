---
name: daf-calendrier
description: Situe la position dans le cycle Daf Yomi — quel daf à quelle date, avancement dans le traité en cours, compte à rebours du siyoum haShas, détection des jalons, rattrapage. Déclencher sur « où en est-on », « quel daf aujourd'hui », « quel daf le 12 octobre », « quand finit-on Bekhorot », « c'est quand le siyoum », « combien reste-t-il ».
---

# Position dans le cycle

## La source est l'API, pas un calcul

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/daf_calendar.py today
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/daf_calendar.py date 2026-10-12
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/daf_calendar.py progress
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/daf_calendar.py jalons 2026-11-18
```

Le daf de chaque date vient de `/api/calendars` de Sefaria. **Il n'y a donc
aucune arithmétique de calendrier, aucun offset, aucune calibration** — et rien
à recaler si l'utilisateur signale un écart : c'est Sefaria qui fait foi. Si un
écart apparaît malgré tout, c'est un bug à investiguer, pas un paramètre à
ajuster.

Pour répondre à « où en est-on », lancer `progress` et **résumer** : le daf du
jour, la position dans le traité, le compte à rebours du siyoum, et le prochain
jalon. Ne pas recopier la sortie brute.

## Le siyoum haShas

`progress` l'affiche. La date est trouvée par **bissection sur l'API** — on
cherche la dernière date qui renvoie encore un daf — et mise en cache dans
`data/cycle.json`. Pour la recalculer :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/daf_calendar.py siyoum
```

Au 23 septembre 2026 : **7 juin 2027, Nidda 73a**.

## Les jalons

`jalons <date>` renvoie `debut_massekhet`, `fin_massekhet`, `debut_seder`,
`fin_seder`, détectés en comparant avec la veille et le lendemain. Pour un
jalon, enchaîner avec `daf-massekhet`.

## Deux cas particuliers à connaître

**Chekalim** est étudié dans le **Yerushalmi** par le cycle Daf Yomi. Pour ces
jours, l'API ne donne pas un amoud mais une **plage de chapitres** du type
`Jerusalem Talmud Shekalim 4:2:15-3:3`. C'est cette référence qui fait foi, pas
le libellé affiché.

**Tamid** n'a pas de pages « background » sur dafyomi.co.il. La collecte le
signale ; ne pas les chercher.

## Régénérer l'index des traités

Seulement si l'on soupçonne un problème :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/build_bavli.py
```

Reconstruit `data/bavli.json` : 38 traités du cycle, avec le dernier daf de
chacun. Sefaria indexant les amudim depuis 1a (folio vide), le dernier daf est
`ceil(longueur / 2)`. Les valeurs sont vérifiables traité par traité contre les
nombres connus — 37 sur 38 concordent, Chekalim étant à part.
