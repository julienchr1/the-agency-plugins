# Routines

Deux routines suffisent. Les jalons — début et fin de traité, hadran, siyoum —
n'ont pas besoin de leur propre déclencheur : ils se **déduisent du calendrier**,
et la routine quotidienne les détecte.

## 1. Quotidienne — la journée complète

**Quand** : tous les jours à 6h30. `30 6 * * *`

```
Lance la skill daf-yomi pour aujourd'hui.

1. Situe le daf du jour et vérifie les jalons.
2. S'il y a une ouverture ou une fin de traité, produis d'abord le bloc
   correspondant avec daf-massekhet.
3. Collecte les sources, rédige le français, assemble les DEUX fiches :
   B (lecture guidée) et B-light (6 pages maximum), chacune en .md et .pdf.
4. Compose le message WhatsApp.
5. Présente-moi : les fichiers produits, ce que dit le daf en deux ou trois
   phrases, et le message prêt à valider.

N'envoie rien. Attends mon accord explicite.
Si un PDF échoue ou si un garde-fou refuse l'assemblage, dis-le — ne présente
pas une fiche incomplète comme terminée.
```

## 2. Monitoring hebdomadaire

**Quand** : chaque dimanche à 8h. `0 8 * * 0`

```
Lance la skill daf-monitoring.

Contrôle : avancement et compte à rebours du siyoum, fiches absentes ou
partielles, jalons des 14 prochains jours, réponse des sources.

Rapport court en français. Si tout est à jour, trois lignes suffisent.
Termine par une ou deux actions concrètes.
```

## Ce que les routines ne font pas

**Elles n'envoient pas le message.** Un envoi à un groupe demande une validation
à chaque fois. La routine s'arrête au message prêt.

## Une note sur le coût

La version B traduit le daf intégralement : environ 18 000 caractères de
français par jour, soit bien plus qu'un programme de michna. Si la charge
devient pesante, **B-light seule reste viable** — elle est indexée sur le
nombre de sugyot, pas sur le volume du texte, et tient ses 6 pages même sur un
daf très dense.
