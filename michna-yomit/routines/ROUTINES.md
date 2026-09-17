# Routines

Quatre routines. Les trois « événements » (début de traité, fin de traité)
n'ont pas de déclencheur propre : dans un cycle à 2 michnaiot par jour, le
jalon est **déductible du calendrier**. Une seule routine quotidienne le
détecte et branche ; c'est plus fiable qu'un cron par événement, qui
supposerait de connaître les dates à l'avance et se désynchroniserait au
premier recalage.

À créer comme Routines Cowork. Le texte de chaque routine est à donner tel
quel comme prompt.

---

## 1. Quotidienne — la journée complète

**Quand** : tous les jours à 6h30. `30 6 * * *`

```
Lance la skill michna-yomit pour la journée d'aujourd'hui.

1. Situe le jour dans le calendrier.
2. Vérifie les jalons du jour avec check.py events. S'il y a une ouverture
   ou une fin de traité, produis d'abord le bloc correspondant avec
   michna-massekhet.
3. Récupère les sources des 2 michnaiot, rédige le français, assemble les
   fiches en .md et en .pdf.
4. Compose le message WhatsApp.
5. Présente-moi : les fichiers produits, une phrase de contenu par michna, et
   le message complet prêt à valider.

N'envoie rien. Attends mon accord explicite pour l'envoi.
Si Sefaria ne répond pas, dis-le et arrête-toi — ne produis pas de fiche
partielle présentée comme complète.
```

---

## 2. Début de massekhet

**Quand** : intégré à la routine quotidienne (étape 2). Peut aussi être lancé
seul.

```
Lance la skill michna-massekhet. Vérifie si un traité s'ouvre aujourd'hui ou
dans les 3 prochains jours. Si oui, produis le bloc d'ouverture : nom et
seder, nombre de chapitres et de michnaiot, durée prévue et date de fin, sujet
du traité, grandes articulations, notions à connaître pour y entrer, et s'il
existe une Guemara dessus.

Sourcé sur Sefaria. Si tu ne peux pas fonder une affirmation, omets-la.
```

---

## 3. Fin de massekhet — siyoum

**Quand** : intégré à la routine quotidienne (étape 2). Peut aussi être lancé
seul.

```
Lance la skill michna-massekhet. Vérifie si un traité s'achève aujourd'hui.
Si oui, produis le bloc de siyoum : le traité achevé, michnaiot et jours
qu'il a pris, récapitulatif en 4 à 6 points de ce qu'il établit (appuie-toi
sur les fiches déjà produites du traité, pas sur ta mémoire), position dans le
cycle après ce traité, et annonce du traité suivant. Si c'est aussi la fin
d'un seder, signale-le.
```

---

## 4. Monitoring hebdomadaire

**Quand** : chaque dimanche à 8h. `0 8 * * 0`

```
Lance la skill michna-monitoring.

Contrôle : avancement, fiches absentes ou incomplètes (en particulier les
sections de Bartenura manquantes), jalons des 14 prochains jours, calibration
du calendrier, et réponse des sources Sefaria et dafyomi.co.il.

Rapport court en français. Si tout est à jour et qu'il n'y a rien à signaler,
trois lignes suffisent. Termine par une ou deux actions concrètes proposées.
```

---

## Créer les routines

Dans Cowork, via l'outil de tâches planifiées. Demander à Claude :

```
Crée les routines du plugin michna-yomit décrites dans routines/ROUTINES.md :
la quotidienne à 6h30 et le monitoring le dimanche à 8h.
```

## Ce que les routines ne font pas

**Elles n'envoient pas le message WhatsApp.** Un envoi à un groupe demande une
validation à chaque fois. La routine s'arrête au message prêt.

Pour un envoi réellement automatique, il faut l'API WhatsApp Business Cloud
(Meta) ou Twilio : compte WhatsApp Business, numéro dédié, token, modèles de
message approuvés. Voir la skill `michna-whatsapp`. Sans cela, le dernier
geste reste manuel — et c'est aussi bien pour un contenu d'étude qu'on relit
avant de diffuser.
