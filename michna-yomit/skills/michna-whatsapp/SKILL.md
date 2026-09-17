---
name: michna-whatsapp
description: Compose le message WhatsApp quotidien de la Michna Yomit (hébreu, traduction française complète, points essentiels, lien vers les fiches) et l'envoie après validation. Déclencher sur « message whatsapp », « le message du jour », « prépare le message pour le groupe », « envoie la michna sur whatsapp ».
---

# Message WhatsApp quotidien

## Composer

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/whatsapp.py --day 2026-09-17
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/whatsapp.py --day 2026-09-17 --lien "https://…" --copier
```

Le script lit les fiches du jour et assemble le message. Il échoue si une
fiche manque : produire les fiches d'abord (`michna-fiche`).

## Format retenu

Compact, mais complet sur l'essentiel. Pour chaque michna :

1. le titre (traité + chapitre:michna) ;
2. le **texte hébreu intégral**, en italique, sur sa propre ligne ;
3. la **traduction française complète** ;
4. les **points essentiels** (les `points_essentiels` du `.fr.json`).

Puis, en pied : le lien ou la mention de la pièce jointe, et le lien Sefaria.
L'en-tête porte la date, le jour du cycle, le pourcentage, et tout jalon
détecté (premier ou dernier jour d'un traité).

Conventions WhatsApp : `*gras*`, `_italique_`. L'italique du `.fr.json`
(`*terme*`) est converti en `_terme_` par le script — ne pas le refaire à la
main.

Si un jalon tombe ce jour-là, faire précéder le message du bloc produit par
`michna-massekhet` (ouverture de traité ou siyoum) plutôt que de l'improviser.

## Le lien vers la fiche complète

Trois options, par ordre de simplicité :

1. **Pièce jointe** — joindre les deux PDF au message. Le plus robuste,
   aucune infrastructure. C'est le défaut quand `--lien` n'est pas donné.
2. **Artifact** — publier une page avec l'outil Artifact et passer son URL à
   `--lien`. Utile pour un groupe qui préfère lire dans le navigateur.
3. **Dossier partagé** — déposer les PDF sur un Drive et passer le lien.

Demander une fois à l'utilisateur ce qu'il préfère, puis s'y tenir.

## Envoi — validation obligatoire

**Ne jamais envoyer sans accord explicite de l'utilisateur, à chaque fois.**
C'est un message adressé à un groupe : afficher le texte intégral, dire à quel
destinataire il partirait, et attendre un oui clair. Un accord donné hier ne
vaut pas pour aujourd'hui.

Moyens d'envoi, à choisir avec l'utilisateur :

- **Semi-automatique (défaut)** — `--copier` met le message dans le
  presse-papiers ; l'utilisateur colle dans WhatsApp et joint les PDF. Un
  seul geste, et il garde la main sur l'envoi.
- **Lien `wa.me`** — ouvrir `https://wa.me/<numéro>?text=<message encodé>`
  pré-remplit la conversation ; l'utilisateur appuie sur envoyer. Ne marche
  pas pour un groupe et ne permet pas la pièce jointe.
- **API WhatsApp Business Cloud (Meta) ou Twilio** — seule voie d'un envoi
  réellement non surveillé. Exige un compte WhatsApp Business, un numéro
  dédié, un token et des modèles de message approuvés. À mettre en place avec
  l'utilisateur ; ne pas le supposer configuré.

Si l'utilisateur veut un envoi automatique complet, le dire franchement : sans
API Business, l'envoi reste un geste manuel, et la routine s'arrête au message
prêt à coller.
