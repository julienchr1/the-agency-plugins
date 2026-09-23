---
name: daf-whatsapp
description: Compose le message WhatsApp quotidien du Daf Yomi et l'envoie après validation. Déclencher sur « message whatsapp », « le message du jour », « prépare le message pour le groupe », « envoie le daf sur whatsapp ».
---

# Message WhatsApp quotidien

## Composer

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/whatsapp.py --jour 2026-09-23 \
  --out messages/2026-09-23.txt
```

Le script lit la fiche du jour et assemble le message. Il échoue si la fiche
manque : produire les fiches d'abord (`daf-fiche`).

## Format

Compact, lisible sur mobile :

1. en-tête — date, daf, position dans le traité, compte à rebours du siyoum ;
2. tout jalon détecté (ouverture, hadran) ;
3. **ce que dit le daf** : les `points_whatsapp` de la fiche ;
4. le lien vers les fiches complètes, ou la mention de la pièce jointe ;
5. le lien Sefaria.

Le daf est trop long pour être cité dans un message : contrairement à la michna,
**on n'y met pas le texte**. C'est la structure et les points saillants qui
passent.

### Emphase : ne rien convertir à la main

Les fiches sont en Markdown (`*terme*` italique, `**mot**` gras) ; WhatsApp
inverse la convention (`*gras*`, `_italique_`). Le script fait la conversion
dans les deux sens, sur tous les champs. Ne pas la refaire — on casserait le
gras.

### Sauvegarder

Utiliser `--out`, jamais une redirection shell. `stdout` ne porte que le
message et les diagnostics sont muets sauf `--verbose`, de sorte qu'une
redirection ne peut pas glisser de ligne parasite dans le fichier.

## Les fiches : pièce jointe ou lien

Deux documents par jour, B et B-light. Le principe retenu : **chacun lit selon
le temps qu'il a**. Les joindre tous les deux, ou pointer une page qui les
porte.

Demander une fois à l'utilisateur ce qu'il préfère, puis s'y tenir.

## Envoi — validation obligatoire

**Ne jamais envoyer sans accord explicite, à chaque fois.** C'est un message
adressé à un groupe : afficher le texte intégral, dire à quel destinataire il
partirait, attendre un oui clair. Un accord donné hier ne vaut pas pour
aujourd'hui.

Sans API WhatsApp Business, l'envoi reste un geste manuel : `--copier` met le
message dans le presse-papiers. Le dire franchement plutôt que de laisser
croire à un envoi automatique.
