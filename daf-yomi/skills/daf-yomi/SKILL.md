---
name: daf-yomi
description: Point d'entrée du Daf Yomi. Fait la journée complète (les deux fiches du daf + le message WhatsApp), répond à « où en est-on », et oriente vers la bonne sous-skill. Déclencher sur « daf yomi », « le daf du jour », « on fait le daf », « où en est-on dans le cycle », « quel daf aujourd'hui », « rattrape les dafim manqués », ou quand la routine quotidienne se déclenche.
---

# Daf Yomi — orchestrateur

Un daf par jour, dans le cycle 14. **La position vient de l'API calendrier de
Sefaria** : il n'y a aucun calcul de calendrier à faire, donc aucune
calibration à surveiller.

## Où les fichiers sont écrits

Le plugin installé est en lecture seule. Fiches et PDF vont dans le **dossier
de travail** : `$DAF_HOME` s'il est défini, sinon le répertoire courant s'il
contient un fichier `.daf-yomi`, sinon `~/Documents/Daf Yomi`.

**Au premier usage dans un dossier de projet**, créer le marqueur avant tout le
reste — sinon les fiches partiront dans `~/Documents/Daf Yomi` :

```bash
touch .daf-yomi
```

## Commencer par situer la journée

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/daf_calendar.py today
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/daf_calendar.py jalons
```

## Aiguillage

| Demande | Skill |
|---|---|
| Faire la journée (deux fiches + message) | rester ici, suivre ci-dessous |
| Un daf précis, refaire une fiche | `daf-fiche` |
| Où en est-on, compte à rebours du siyoum | `daf-calendrier` |
| Approfondir une sugya, Rashi, Tossafot | `daf-sugya` |
| Début de traité, hadran, siyoum | `daf-massekhet` |
| Message WhatsApp | `daf-whatsapp` |
| Contrôle hebdomadaire | `daf-monitoring` |

## La journée complète

1. **Situer** — `daf_calendar.py today`, puis `jalons`. Si un jalon tombe
   aujourd'hui (début ou fin de traité), enchaîner avec `daf-massekhet`
   **avant** de composer le message.

2. **Collecter** —
   `python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/fetch_daf.py --jour <date>`
   Lire ensuite le `.source.json` en entier. Il donne le nombre de segments par
   amoud, les dibbourim de Rashi et Tossafot, le glossaire du Kollel et les
   difficultés.

3. **Rédiger et assembler** — appliquer `daf-fiche`. Les deux documents
   doivent sortir : **B** et **B-light**, chacun en `.md` et en `.pdf`.

4. **Message** — appliquer `daf-whatsapp`.

5. **Rendre compte** — les fichiers produits, ce que dit le daf en deux ou
   trois phrases, et le message prêt à valider. Si un PDF a échoué, le dire.

## Rattrapage

Traiter du plus ancien au plus récent, un daf à la fois. Ne pas fusionner
plusieurs dafim dans une même fiche : le daf est l'unité.

## Règles

- Ne jamais écrire d'araméen de mémoire. Le texte vient de la collecte, et le
  script l'insère lui-même dans les fiches.
- Ne jamais envoyer un message sans validation explicite.
- Si Sefaria est injoignable, le dire et s'arrêter — pas de fiche partielle
  présentée comme complète.
