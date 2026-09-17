---
name: michna-monitoring
description: Contrôle hebdomadaire du programme Michna Yomit — avancement, fiches manquantes ou incomplètes, jalons à venir, santé des sources Sefaria et dafyomi.co.il, dérive éventuelle du calendrier. Déclencher sur « monitoring », « contrôle du programme », « est-ce qu'il manque des fiches », « bilan de la semaine », « tout est à jour ? », ou quand la routine hebdomadaire se déclenche.
---

# Monitoring du programme

À lancer une fois par semaine, ou dès qu'on soupçonne un trou.

## 1. Avancement

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py progress
```

## 2. Intégrité des fiches

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/check.py audit --from 2026-09-01      # ou sans --from : tout
```

Trois états : complète, incomplète (il manque le `.md`, le `.pdf`, ou des
sections du Bartenura), absente. Les sections de Bartenura manquantes sont le
défaut le plus important : une fiche dont le Bartenura est partiel ne remplit
pas son objet.

## 3. Jalons à venir

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/check.py events <date>
```

Regarder les 10 à 14 jours qui viennent et lister les ouvertures et fins de
traité, ainsi que les changements de seder.

## 4. Calendrier toujours aligné

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py build
```

La sortie vérifie la calibration. Si elle affiche `ECART`, comparer avec la
page de référence du 16ᵉ cycle Mishnah Yomi
(<https://www.dafyomi.co.il/calendars/myomi/todays_mishnah.php>) et recaler
via `michna-calendrier`.

## 5. Santé des sources

Vérifier que les deux sources répondent :

```bash
curl -s -o /dev/null -w "sefaria %{http_code}\n" \
  "https://www.sefaria.org/api/shape/Mishnah%20Berakhot"
curl -s -o /dev/null -w "dafyomi %{http_code}\n" \
  "https://www.dafyomi.co.il/chulin/backgrnd/ch-in-140.htm"
```

Si Sefaria a changé un titre d'ouvrage, `build_index.py` le signale en
échouant sur le traité concerné : le relancer permet de détecter la dérive
tôt.

## Le rapport

Un rapport court, en français, dans cet ordre :

1. **Position** — jour du cycle, michna du jour, pourcentage, traité en cours.
2. **À traiter** — les fiches absentes ou incomplètes, avec leur date. S'il n'y
   a rien, le dire en une ligne.
3. **À venir** — les jalons des deux prochaines semaines.
4. **Technique** — calibration, état des sources. Uniquement s'il y a un
   problème ; sinon une ligne.
5. **Ce que je propose** — une ou deux actions concrètes, pas une liste.

Ne pas produire un rapport si tout va bien et qu'il n'y a rien à signaler :
dans ce cas, trois lignes suffisent.
