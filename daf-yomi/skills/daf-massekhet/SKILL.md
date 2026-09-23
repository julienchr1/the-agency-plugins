---
name: daf-massekhet
description: Gère les jalons du cycle Daf Yomi — ouverture d'un traité (présentation, thèmes, durée) et achèvement d'un traité avec le hadran et le siyoum, ainsi que les passages d'un seder à l'autre et le siyoum haShas. Déclencher sur « début de massekhet », « on commence quel traité », « on finit Bekhorot », « hadran », « siyoum », « présente le traité », ou quand la routine détecte un jalon.
---

# Jalons : ouverture et achèvement d'un traité

Sur un cycle à un daf par jour, un jalon revient toutes les quelques semaines —
bien plus souvent que dans un cycle de michna. C'est un moment social autant
qu'intellectuel.

## Détecter

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/daf_calendar.py jalons 2026-11-18
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/daf_calendar.py progress
```

Types renvoyés : `debut_massekhet`, `fin_massekhet` (avec le traité suivant),
`debut_seder`, `fin_seder`.

Un même jour ne porte qu'un daf, donc début et fin de traité tombent sur deux
jours consécutifs — jamais sur le même, contrairement à un programme à deux
portions.

## Ouverture d'un traité

Produire un bloc court, lisible sur WhatsApp :

- nom du traité en français et en hébreu, seder ;
- **nombre de dafim et durée** : `dernier_daf - 1` dafim, donc autant de jours ;
- date de fin prévue — la calculer avec `daf_calendar.py date` ;
- **de quoi traite le traité** : le sujet central, en 3 à 5 phrases ;
- les grandes articulations, si on peut les fonder ;
- ce qu'il faut savoir pour y entrer : vocabulaire, realia, notions supposées.

Sourcer la présentation. L'introduction du traité sur Sefaria et la structure
par chapitres sont des appuis légitimes. **Ne pas inventer de découpage
thématique** : si on ne peut pas le fonder, l'omettre.

## Achèvement — hadran et siyoum

Produire un bloc de siyoum :

- le traité achevé, le nombre de dafim et de jours, les dates de début et de fin ;
- un récapitulatif en 4 à 6 points de ce que le traité a établi — pas un
  sommaire des chapitres, mais ce qu'on en retient. **S'appuyer sur les fiches
  déjà produites** (`fiches/*_B-light.md`) plutôt que sur la mémoire ;
- la position dans le cycle : dafim faits, pourcentage, traités achevés,
  **compte à rebours du siyoum haShas** ;
- l'annonce du traité suivant en une ou deux phrases ;
- s'il s'agit aussi d'une fin de seder, le dire.

La formule du **hadran** (הדרן עלך) se dit à l'achèvement d'un traité. La citer
telle quelle si l'utilisateur la veut dans le message, sans la paraphraser.

## Le siyoum haShas

La fin du cycle est un jalon d'une autre nature. Au 23 septembre 2026 :
**7 juin 2027, Nidda 73a**. À l'approche, le rappeler dans les messages — le
compte à rebours est déjà dans l'en-tête des fiches.

## Remise au message du jour

Ces blocs sont destinés à être placés en tête du message WhatsApp par
`daf-whatsapp`. Les produire, puis enchaîner — ne pas envoyer directement.
