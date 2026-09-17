---
name: michna-yomit
description: Point d'entrée du programme Michna Yomit. Fait la journée complète (les 2 fiches du jour + le message WhatsApp), répond à « où en est-on », et oriente vers la bonne sous-skill. Déclencher sur « michna yomit », « la michna du jour », « on fait la michna », « où en est-on dans le programme », « michna d'aujourd'hui », « rattrape les jours manqués », ou quand la routine quotidienne se déclenche.
---

# Michna Yomit — orchestrateur

Programme : **2 michnaiot par jour, tous les jours**, démarré le
**16 juillet 2025** à Zeva'him 1:1, avec pour objectif les **63 traités /
4192 michnaiot** de la Michna. Voir `references/programme.md`.

## Où les fichiers sont écrits

Le plugin installé est en lecture seule. Fiches, calendrier et calibration
vont dans le **dossier de travail**, résolu dans cet ordre :

1. `$MICHNA_HOME` ;
2. un fichier `.michna-yomit` dans le répertoire courant ;
3. le répertoire courant s'il contient déjà `data/program.json` ;
4. `~/Documents/Michna Yomit`.

**Au premier usage dans un dossier de projet**, si aucune de ces conditions
n'est remplie, créer le marqueur avant tout le reste — sinon les fiches
partiront dans `~/Documents/Michna Yomit` et l'utilisateur les cherchera
ailleurs :

```bash
touch .michna-yomit
```

Le dossier de travail s'amorce ensuite tout seul (les données de référence du
plugin y sont recopiées).

## Commencer par situer la journée

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py today
```

Cela donne le jour, les deux références, et la position dans le cycle. Si la
date du jour n'est pas dans le calendrier, c'est que le programme est terminé
ou que le calendrier doit être régénéré (`build`).

## Aiguillage

| Demande | Skill |
|---|---|
| Faire la journée (2 fiches + message) | rester ici, suivre ci-dessous |
| Une michna précise, ou refaire une fiche | `michna-fiche` |
| Où en est-on, avancement, recaler le calendrier | `michna-calendrier` |
| Composer / envoyer le message WhatsApp | `michna-whatsapp` |
| Début de traité, fin de traité, siyoum | `michna-massekhet` |
| Les sujets de Guemara sur cette michna | `michna-guemara` |
| Contrôle hebdomadaire, trous, dérive | `michna-monitoring` |

## La journée complète

1. **Situer** — `calendar_build.py today`. Signaler tout jalon : premier jour
   d'un traité, dernier jour d'un traité, passage d'un seder à l'autre. Si un
   jalon tombe aujourd'hui, enchaîner avec `michna-massekhet` **avant** de
   composer le message, pour qu'il en porte la mention.

2. **Sources** — `python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/fetch_mishna.py --day <date>`.

3. **Fiches** — appliquer `michna-fiche` pour chacune des deux michnaiot :
   rédiger le `.fr.json`, puis `python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/build_fiche.py --day <date>`.
   Les deux fiches doivent sortir en `.md` **et** en `.pdf`.

4. **Message** — appliquer `michna-whatsapp`.

5. **Rendre compte** — les fichiers produits, une phrase de contenu par
   michna, et le message prêt à valider. Si le PDF a échoué, le dire.

## Rattrapage

Pour des jours manqués, traiter du plus ancien au plus récent, une journée à
la fois, sans fusionner les fiches. Le message WhatsApp ne porte que sur la
journée du jour ; pour le retard, proposer un message de rattrapage distinct
plutôt que d'empiler plusieurs jours dans un seul message.

## Règles

- Ne jamais écrire de texte hébreu ou de citation de Bartenura de mémoire :
  tout passe par Sefaria.
- Ne jamais envoyer un message sans validation explicite (cf.
  `michna-whatsapp`).
- Si Sefaria est injoignable, le dire et s'arrêter — ne pas produire une fiche
  partielle en la présentant comme complète.
