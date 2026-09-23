---
name: daf-fiche
description: Produit les deux fiches d'étude d'un daf — B, lecture guidée avec le texte araméen traduit intégralement et organisé par sugya, et B-light, exposé de la structure en 6 pages maximum — en Markdown et en PDF. Déclencher sur « fiche du daf », « prépare le daf du jour », « fais-moi Bekhorot 5 », « refais la fiche de ... », ou quand une autre skill du plugin demande une fiche.
---

# Les deux fiches d'un daf

Un daf produit **deux documents**, depuis une seule source :

| | contenu | plafond |
|---|---|---|
| **B** | araméen intégral **traduit segment par segment**, organisé par sugya, Rashi et Tossafot, glossaire | aucun |
| **B-light** | la structure et l'exposé de l'argument, citations choisies | **6 pages** |

## Principe non négociable

**Ne jamais saisir d'araméen.** Le texte est lu depuis la collecte et inséré
par le script. Une citation se désigne par son amoud et son numéro de segment,
jamais par son texte. C'est ce qui rend une citation inexacte impossible.

## Étape 1 — Collecter

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/fetch_daf.py --jour 2026-09-23
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/fetch_daf.py "Bekhorot 5"
```

Écrit `fiches/<slug>.source.json` : araméen segmenté, traduction Davidson
d'appui, **Rashi et Tossafot par l'API links**, glossaire indexé par ligne et
variantes textuelles du Kollel Iyun Hadaf, difficultés (insights).

Lire le fichier en entier avant de rédiger. Noter en particulier
`couverture` : le nombre réel de dibbourim de Rashi et Tossafot sur **ce** daf.
Cette couverture se **constate**, elle ne se promet pas.

## Étape 2 — Rédiger le français

Écrire `fiches/<slug>.fr.json` :

```json
{
  "libelle": "Bekhorot 5",
  "titre_court": "le sujet du daf en une ligne",
  "avant_douvrir": "2 à 4 paragraphes : d'où vient le daf, où est la michna, ce qui fait charnière",
  "traduction": { "5a": ["…", "…"], "5b": ["…"] },
  "sugyot": [
    {
      "n": 1, "titre": "…", "loc": "5a:1–7", "nature": "débat amoraïque",
      "intro": "2 à 4 phrases — ce que cherche la sugya (pour B)",
      "expose": "le déroulé de l'argument, en markdown (pour B-light)",
      "citations": [{"amud": "5a", "seg": 3, "rendu": "rendu français bref"}],
      "tableaux": [{"titre": "…", "colonnes": ["…"], "lignes": [["…"]]}],
      "difficulte": {"titre": "…", "question": "…", "reponses": ["…"]}
    }
  ],
  "difficultes_en_renvoi": ["titre des difficultés non reprises"],
  "glossaire": [{"he": "…", "ligne": "5a, 27", "sens": "…"}],
  "girsa": ["…"],
  "a_retenir": ["4 à 6 puces"],
  "points_whatsapp": ["2 à 3 puces — servent au message"]
}
```

### `traduction` — pour B

Un tableau par amoud, **exactement autant d'entrées que de segments**
(`n_segments` dans la collecte). Traduction suivie, fidèle, dans l'ordre. Ne
pas lisser un désaccord, ne pas trancher ce que le daf laisse ouvert. Les
termes techniques sont translittérés *en italique* et glosés une fois.

L'anglais de la collecte (Davidson) est un appui, pas la source : traduire
depuis l'araméen et n'utiliser l'anglais que pour lever un doute.

### `sugyot` — la structure

Découper le daf en mouvements réels. Un daf en a typiquement de 3 à 11. Pour
chacun : ce qu'il cherche, comment l'argument avance, et où il aboutit.

`intro` sert B, `expose` sert B-light. `expose` est **un exposé, pas une
traduction** : il rend compte de l'argument.

### Ce qui fait tenir B-light en 6 pages

Deux règles, sans lesquelles le format dérape :

1. **une seule `difficulte` dans tout le fichier.** Les autres vont dans
   `difficultes_en_renvoi`. Le script refuse d'assembler au-delà.
2. **un tableau dès trois avis ou plus.** Cinq opinions sur un nom, trois
   tentatives de dérivation, deux manières de lire : en tableau, pas en prose.

Et 4 à 6 citations pour tout le daf, pas davantage.

### `glossaire` et `girsa`

Tirés de `background` dans la collecte, dont les entrées sont **indexées par
numéro de ligne** du daf. Ne retenir que ce qui sert la lecture. La section
girsa donne les corrections du Bach et du Vilna Shas, que Sefaria ne porte pas.

### `difficulte`

Tirée de `insights`. Chaque item a un titre, une question et des réponses, avec
les sources nommées (Tossafot, Chitta Mekoubetset…). Reprendre **la plus
substantielle**, renvoyer les autres.

Attention : si un item porte `tronque: true`, son corps a été coupé à 6 000
caractères — consulter l'URL pour la suite.

## Étape 3 — Assembler

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/build_fiche.py --jour 2026-09-23
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/build_fiche.py "Bekhorot 5" --only light
```

Le script **refuse d'assembler** plutôt que de livrer du faux :

- une traduction incomplète ou avec un segment vide ;
- une citation qui pointe un segment inexistant ;
- plus d'une difficulté retenue ;
- B-light au-delà de 6 pages.

Ne pas contourner un refus : corriger le `.fr.json`.

Le PDF passe par Chrome ou Chromium, cherché dans `$DAF_CHROME`, puis dans
`/Applications`, puis dans le `PATH` — ce dernier cas étant celui des
conteneurs Linux. Un PDF contenant une page d'erreur de navigateur est rejeté.

## Étape 4 — Contrôler avant de livrer

- les deux `.pdf` existent ;
- B-light ne dépasse pas 6 pages **dans le PDF** (le script le signale) ;
- l'araméen s'affiche de droite à gauche et n'est pas coupé ;
- la couverture Rashi/Tossafot annoncée correspond à `couverture`.

Annoncer ensuite les fichiers produits et, en deux ou trois phrases, ce que dit
le daf. Ne jamais dire qu'une fiche est prête si un PDF a échoué.
