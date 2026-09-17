---
name: michna-massekhet
description: Gère les jalons du cycle Michna Yomit — ouverture d'un traité (présentation, thèmes, durée) et achèvement d'un traité (récapitulatif, message de siyoum, annonce du suivant), ainsi que les passages d'un seder à l'autre. Déclencher sur « début de massekhet », « on commence quel traité », « on finit Ohalot », « siyoum », « présente le traité », « fin de traité », ou quand la routine détecte un jalon.
---

# Jalons : ouverture et achèvement d'un traité

## Détecter

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/check.py events 2026-11-17
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/check.py tractate "Mishnah Oholot"
```

`events` renvoie les jalons de la date : `debut_massekhet`, `fin_massekhet`,
`debut_seder`, `fin_seder`. S'il n'y en a aucun, il indique combien de jours
restent dans le traité en cours — utile pour annoncer à l'avance.

Un jour peut porter **deux** jalons à la fois : la dernière michna d'un traité
et la première du suivant tombent souvent le même jour, puisque le programme
avance par paires.

## Ouverture d'un traité

Produire un bloc court (10–15 lignes), adapté à une lecture sur WhatsApp :

- nom du traité en français et en hébreu, seder ;
- nombre de chapitres et de michnaiot, durée prévue dans le cycle et date de
  fin (donnés par `check.py`) ;
- **de quoi traite le traité** : sujet central, en 3 à 5 phrases ;
- les grandes articulations (les blocs de chapitres et leur objet) ;
- ce qu'il faut savoir pour entrer dedans : vocabulaire, unités de mesure,
  realia, notions présupposées ;
- s'il y a une Guemara sur ce traité, le signaler.

Sourcer cette présentation. Deux appuis fiables :

- l'introduction de Sefaria au traité, si elle existe :
  `https://www.sefaria.org/api/texts/English_Explanation_of_<traité>.1.1`
  (le premier paragraphe est souvent une introduction) ;
- `https://www.sefaria.org/api/index/<traité>` pour la structure.

Ne pas inventer de découpage thématique : le déduire des titres de chapitres
et du contenu réellement consulté. Si l'on ne peut pas fonder une
affirmation, l'omettre.

## Achèvement d'un traité — siyoum

Produire un bloc de siyoum :

- le traité achevé, le nombre de michnaiot et de jours qu'il a pris, les dates
  de début et de fin ;
- un récapitulatif en 4 à 6 points de ce que le traité a établi — pas un
  sommaire des chapitres, mais ce qu'on en retient ;
- la position dans le cycle après ce traité : combien de michnaiot faites sur
  4192, quel pourcentage, combien de traités achevés ;
- l'annonce du traité suivant, en une ou deux phrases (le bloc d'ouverture
  complet part le jour où il commence) ;
- s'il s'agit aussi de la fin d'un seder, le dire — c'est un jalon plus fort.

Pour le récapitulatif, s'appuyer sur les fiches déjà produites du traité
(`fiches/*.md`) plutôt que sur la mémoire : elles contiennent ce qui a
réellement été étudié.

## Remise au message du jour

Ces blocs sont destinés à être placés en tête du message WhatsApp du jour par
`michna-whatsapp`. Les produire, puis enchaîner — ne pas envoyer directement.
