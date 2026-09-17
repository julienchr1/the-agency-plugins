---
name: michna-fiche
description: Produit la fiche d'étude complète d'une michna — texte hébreu intégral, traduction française, explication en français, la TOTALITÉ des sections du Bartenura en hébreu avec leur traduction française intégrale, et les renvois au Talmud — en Markdown, HTML et PDF. Tout est sourcé sur Sefaria. Déclencher sur « fiche michna », « prépare la michna du jour », « fais-moi Ohalot 2:4 », « la fiche de Zeva'him 3:1 », « refais la fiche de ... », ou quand une autre skill du plugin demande une fiche.
---

# Fiche d'étude d'une michna

Une fiche = un fichier par michna, en trois formats (`.md`, `.html`, `.pdf`).
Le programme avance par paires : une journée produit **deux** fiches.

## Principe non négociable

Les textes (hébreu de la michna, hébreu du Bartenura, appuis anglais) sont
**récupérés depuis Sefaria**, jamais écrits de mémoire. Le français
(traduction, explication) est **rédigé d'après ces sources** et n'est jamais
présenté comme un texte de Sefaria. Si une source est indisponible, le dire
dans la fiche — ne jamais combler par de la mémoire.

## Étape 1 — Récupérer les sources

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/fetch_mishna.py "Mishnah Oholot 2:4"     # une michna
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/fetch_mishna.py --day 2026-09-17          # les 2 du jour
```

Écrit `fiches/<slug>.source.json` avec : hébreu de la michna, traduction
anglaise (William Davidson + Dr. Joshua Kulp), explication anglaise suivie de
Kulp, **toutes** les sections du Bartenura (hébreu et anglais alignés, lemme
séparé du commentaire), les folios du Talmud liés et les URL
« background » de dafyomi.co.il.

Si le script ne peut pas tourner, récupérer à la main — voir
`references/sefaria-api.md` pour les endpoints exacts (tous vérifiés).

Lire ensuite le `.source.json` en entier avant de rédiger. Le nombre de
sections du Bartenura y figure (`bartenura.n_sections`) : c'est le nombre de
traductions à produire, sans exception.

## Étape 2 — Rédiger le français

Écrire `fiches/<slug>.fr.json` :

```json
{
  "ref": "Mishnah Oholot 2:4",
  "titre_court": "Le sujet de la michna, en une ligne",
  "traduction": "Traduction française complète et fidèle de la michna.",
  "contexte": "2 à 4 phrases : de quoi parle le chapitre, ce qui précède.",
  "explication": ["Paragraphe 1.", "Paragraphe 2.", "…"],
  "bartenura": [
    {"n": 1, "traduction": "Traduction française de la section 1.",
     "note": "facultatif : précision utile"}
  ],
  "points_essentiels": ["3 à 4 puces — servent au message WhatsApp"]
}
```

### Règles de traduction

- **Fidélité d'abord.** Traduire ce que dit le texte, dans son ordre. Ne pas
  lisser un désaccord entre Tannaïm, ne pas trancher ce que la michna laisse
  ouvert.
- **Michna** : traduction suivie, phrase par phrase. Les termes techniques sans
  équivalent français sont translittérés *en italique* puis glosés une fois
  entre parenthèses — `*golel*` (la pierre qui ferme le tombeau). Ensuite on
  réutilise le terme translittéré.
- **Bartenura** : **une section du `.source.json` = une entrée dans
  `bartenura`**, traduite intégralement. Ne jamais fusionner deux sections, ne
  jamais en résumer une, ne jamais en sauter une — même très courte
  (« car ils n'atteignent pas la mesure requise » est une section entière et
  suffit). L'anglais du `.source.json` est un appui, pas la source : traduire
  depuis l'hébreu et n'utiliser l'anglais que pour lever un doute.
- **Versets** : garder la référence donnée par le Bartenura, en français
  (Genèse 29:3, Nombres 19:18). Vérifier le livre et le chapitre dans le texte
  hébreu — les éditions abrègent parfois différemment.
- **Explication** : 3 à 5 paragraphes. Partir de l'explication de Kulp et du
  Bartenura pour dégager la logique : quel est le problème, quelles positions
  s'opposent, sur quoi elles s'appuient, ce que tranche la halakha quand le
  Bartenura le dit. Expliquer ce qui n'est pas évident pour un lecteur
  francophone (unités de mesure, realia, vocabulaire d'impureté).
- Ne pas invoquer de commentateur absent du `.source.json`. Pour élargir,
  utiliser la skill `michna-guemara`.
- Translittération : suivre `references/translitteration-fr.md`.

## Étape 3 — Assembler

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/build_fiche.py --day 2026-09-17     # ou "Mishnah Oholot 2:4"
```

Produit `.md`, `.html` et `.pdf`. Le script **refuse d'assembler** si une
section du Bartenura n'a pas sa traduction : c'est le garde-fou, ne pas le
contourner. S'il refuse, compléter le `.fr.json`.

Le PDF est rendu via Chrome headless (mise en page A4, hébreu en RTL). Si aucun
convertisseur n'est disponible, le script le signale et produit quand même
`.md` et `.html` — l'annoncer plutôt que de faire silence.

## Étape 4 — Contrôler avant de livrer

- Le nombre de sections traduites égale `bartenura.n_sections`.
- L'hébreu de la fiche est identique à celui de Sefaria (aucune retouche).
- Chaque terme translittéré est glosé à sa première occurrence.
- Les liens de source en pied de fiche fonctionnent.
- Le PDF existe et l'hébreu s'y affiche de droite à gauche.

Annoncer ensuite les fichiers produits, et pour chaque michna une phrase sur
son contenu. Ne jamais dire qu'une fiche est prête si le PDF a échoué.
