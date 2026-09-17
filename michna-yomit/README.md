# michna-yomit

Plugin d'étude quotidienne de la Michna, entièrement sourcé sur
[Sefaria](https://www.sefaria.org), avec les notions de fond de
[dafyomi.co.il](https://www.dafyomi.co.il) en complément.

## Ce qu'il fait

1. **Une fiche complète par michna** — texte hébreu intégral, traduction
   française, explication en français, **la totalité des sections du
   Bartenura** en hébreu avec leur traduction française intégrale, renvois au
   Talmud. En `.md`, `.html` et `.pdf`.
2. **Deux michnaiot par jour**, selon le calendrier du programme.
3. **Le calendrier du programme** — 63 traités, 4192 michnaiot, du
   16 juillet 2025 au 11 avril 2031 ; interrogeable (« où en est-on »,
   avancement par traité) et recalibrable.
4. **Le message WhatsApp quotidien**, prêt à valider puis à envoyer.
5. **Les jalons du cycle** — ouverture de traité, siyoum, changement de seder.
6. **Un monitoring hebdomadaire** — trous, fiches incomplètes, dérive.

## Les 7 skills

| skill | rôle |
|---|---|
| `michna-yomit` | point d'entrée : la journée complète, l'aiguillage |
| `michna-fiche` | la fiche d'une michna (le cœur) |
| `michna-calendrier` | calendrier, avancement, recalage |
| `michna-whatsapp` | message quotidien, envoi après validation |
| `michna-massekhet` | ouverture de traité, siyoum |
| `michna-guemara` | sujets de Guemara sur une michna |
| `michna-monitoring` | contrôle hebdomadaire |

## Architecture

Le partage des rôles est délibéré :

- **Les scripts font ce qui doit être exact** : arithmétique du calendrier,
  appels API, découpage des sections du Bartenura, assemblage, rendu PDF.
  Déterministe, rejouable, vérifiable.
- **Claude fait ce qui demande du jugement** : la traduction française,
  l'explication, la synthèse. C'est précisément ce qui n'existe pas dans les
  sources — il n'y a quasiment aucune traduction française de la Michna sur
  Sefaria.
- **Le script refuse d'assembler une fiche incomplète.** Si une section du
  Bartenura n'a pas sa traduction, `build_fiche.py` s'arrête. C'est le
  garde-fou contre la fiche qui « a l'air » complète.

```
data/tractates.json      63 traités, michnaiot par chapitre (API /shape)
data/program.json        définition du programme + calibration
data/calendar.json       2097 jours, généré
data/dafyomi_slugs.json  37 traités du Bavli, chaque URL vérifiée en HTTP

fiches/<ref>.source.json  matériel Sefaria brut        (script)
fiches/<ref>.fr.json      le français                  (Claude)
fiches/<ref>.md/.html/.pdf la fiche                    (script)
```

## Dossier de travail

Le plugin installé est une copie **en lecture seule** dans le cache de Claude
Code, effacée à chaque mise à jour. Les fiches, le calendrier et la
calibration sont donc écrits ailleurs — dans le *dossier de travail*, résolu
dans cet ordre :

1. `$MICHNA_HOME` ;
2. un fichier `.michna-yomit` dans le répertoire courant (vide = travailler
   ici ; sinon il contient le chemin voulu) ;
3. le répertoire courant s'il contient déjà `data/program.json` ;
4. `~/Documents/Michna Yomit` (défaut).

Au premier usage, les données de référence livrées avec le plugin (les 63
traités, la table dafyomi, le programme et le calendrier) y sont recopiées,
puis c'est cette copie qui fait foi. Les données du plugin restent intactes.

Pour travailler dans un projet donné — la façon recommandée, notamment dans
Claude Cowork — poser le marqueur à la racine du projet :

```bash
touch .michna-yomit
```

Les scripts s'appellent par un chemin absolu, jamais en relatif :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/calendar_build.py today
```

Les fiches d'exemple livrées dans `fiches/` (Ohalot 2:4 et 2:5) sont des
échantillons : elles montrent le format attendu et ne sont pas le dossier de
travail.

## Scripts

```bash
python3 scripts/build_index.py                      # index des 63 traités
python3 scripts/build_dafyomi_slugs.py              # table dafyomi vérifiée
python3 scripts/calendar_build.py build|today|date|progress|find|calibrate
python3 scripts/fetch_mishna.py "Mishnah Oholot 2:4" | --day 2026-09-17
python3 scripts/build_fiche.py --day 2026-09-17     # .md + .html + .pdf
python3 scripts/whatsapp.py --day 2026-09-17 --copier
python3 scripts/check.py events|tractate|audit
```

Aucune dépendance Python externe. Le PDF passe par Chrome headless (ou
weasyprint / wkhtmltopdf si présents).

## Le programme

Départ **16 juillet 2025** à Zeva'him 1:1, 2 michnaiot par jour, tous les
jours. Ordre : Kodachim (depuis Zeva'him) → Taharot → Zeraïm → Moëd → Nachim
→ Nezikin. Fin prévue le **11 avril 2031**.

Le calendrier est **calibré sur la position réellement étudiée par
l'utilisateur**, jamais sur un calendrier externe — le cycle « Mishnah Yomi »
de dafyomi.co.il en est proche mais décalé d'une michna. L'observation de
référence est conservée dans `data/program.json` et revérifiée à chaque
génération. Détail dans `references/programme.md`.

## Vérifié le 17 septembre 2026

- 63 traités, 4192 michnaiot, **Bartenura disponible pour les 63**.
- Bartenura récupéré **section par section**, hébreu et anglais alignés, lemme
  séparé du commentaire.
- Table dafyomi.co.il : **37 traités du Bavli**, chaque slug validé par une
  requête HTTP. Tamid n'a pas de pages « background » sur le site.
- Le calendrier calibré reproduit la position réelle de l'utilisateur
  (Ohalot 2:5-6 le 17 septembre 2026).
- Chaîne complète exécutée sur Ohalot 2:4 et 2:5 (échantillons) : sources, français, `.md`,
  `.html`, `.pdf` (4 pages, hébreu en RTL, polices embarquées).

## Points ouverts

- **Envoi WhatsApp.** Sans API WhatsApp Business Cloud ou Twilio, l'envoi
  reste un geste manuel (message copié dans le presse-papiers, PDF en pièce
  jointe). À décider : rester en semi-automatique, ou monter un compte
  Business.
- **Le lien « fiche complète »** dans le message : pièce jointe PDF (défaut),
  Artifact publié, ou dossier partagé.
- **Rattrapage** des fiches antérieures au 17 septembre 2026 : 428 jours déjà
  parcourus n'ont pas de fiche. À faire à la demande, ou pas du tout.

## Sources et attribution

- Textes hébreux et traductions anglaises : Sefaria (domaine public / CC-BY-NC
  selon la version ; chaque fiche porte ses liens de source).
- Notions de fond : Kollel Iyun Hadaf, dafyomi.co.il.
- Le français est rédigé d'après ces sources. Ce n'est pas une traduction
  publiée, et chaque fiche le mentionne.
