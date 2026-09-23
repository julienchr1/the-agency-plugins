---
name: daf-monitoring
description: Contrôle hebdomadaire du Daf Yomi — avancement, fiches manquantes ou incomplètes, jalons à venir, santé des sources Sefaria et dafyomi.co.il. Déclencher sur « monitoring », « contrôle du daf », « est-ce qu'il manque des fiches », « bilan de la semaine », « tout est à jour ? », ou quand la routine hebdomadaire se déclenche.
---

# Monitoring

## 1. Position

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/daf_calendar.py progress
```

## 2. Intégrité des fiches

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/check.py audit --from 2026-09-01
```

Quatre états par daf : complet (les deux PDF), partiel (B ou B-light manquant),
français absent, collecte absente. Les fiches **partielles** sont le défaut le
plus courant : un PDF a échoué sans que ce soit relevé.

## 3. Jalons à venir

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/check.py jalons --jours 14
```

## 4. Santé des sources

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/check.py sources
```

Vérifie que Sefaria répond, que le calendrier renvoie bien un daf pour
aujourd'hui, et qu'une page du Kollel Iyun Hadaf est joignable.

À surveiller en particulier : l'approche de la **fin de cycle**. Passé le
7 juin 2027, l'API renverra `None` — le cycle 15 devra être pris en compte.

## Le rapport

Court, en français, dans cet ordre :

1. **Position** — daf du jour, traité, compte à rebours du siyoum.
2. **À traiter** — fiches absentes ou partielles, avec leur date. S'il n'y a
   rien, une ligne suffit.
3. **À venir** — les jalons des deux prochaines semaines.
4. **Technique** — seulement s'il y a un problème.
5. **Ce que je propose** — une ou deux actions concrètes.

Si tout est à jour, trois lignes suffisent. Ne pas produire un rapport pour
dire qu'il n'y a rien à dire.
