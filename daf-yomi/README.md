# daf-yomi

Étude quotidienne du Daf Yomi, sourcée sur [Sefaria](https://www.sefaria.org)
et sur le [Kollel Iyun Hadaf](https://www.dafyomi.co.il).

## Ce qu'il produit

**Deux fiches par jour**, pour que chacun lise selon le temps qu'il a :

| | contenu | taille |
|---|---|---|
| **B** | araméen intégral traduit segment par segment, organisé par sugya, Rashi et Tossafot, glossaire, variantes | ~15 pages |
| **B-light** | la structure et l'exposé de l'argument, citations choisies, tableaux | **6 pages max** |

Chacune en Markdown, HTML et PDF.

## Le calendrier n'est pas calculé

La position vient de l'API `/calendars` de Sefaria, pour n'importe quelle date.
**Aucune arithmétique, donc aucune calibration à surveiller.** La fin du cycle
est trouvée par bissection — au 23 septembre 2026 : **7 juin 2027, Nidda 73a**.

## Les 7 skills

| skill | rôle |
|---|---|
| `daf-yomi` | point d'entrée : la journée, l'aiguillage |
| `daf-fiche` | les deux fiches (le cœur) |
| `daf-calendrier` | position, siyoum, jalons |
| `daf-sugya` | approfondir une sugya, Rashi, Tossafot |
| `daf-massekhet` | ouverture de traité, hadran, siyoum |
| `daf-whatsapp` | message du jour |
| `daf-monitoring` | contrôle hebdomadaire |

## Les garde-fous

Le partage des rôles : les scripts font ce qui doit être exact, Claude fait ce
qui demande du jugement. Et le script **refuse d'assembler plutôt que de livrer
du faux** :

1. **l'araméen n'est jamais saisi.** Une citation se désigne par son amoud et
   son numéro de segment ; le script va chercher le texte dans la collecte. Une
   citation inexacte est donc structurellement impossible ;
2. B exige une traduction pour **chaque** segment de chaque amoud ;
3. une seule difficulté retenue par fiche ;
4. B-light plafonnée à 6 pages ;
5. un PDF contenant une page d'erreur de navigateur est rejeté.

Les cinq ont été testés en les faisant échouer volontairement.

## Dossier de travail

Le plugin installé est en lecture seule. Les fiches vont dans `$DAF_HOME`,
sinon le répertoire courant s'il contient un fichier `.daf-yomi`, sinon
`~/Documents/Daf Yomi`.

```bash
touch .daf-yomi      # à la racine du dossier de projet, au premier usage
```

## Scripts

```bash
python3 scripts/daf_calendar.py today|date|progress|jalons|siyoum
python3 scripts/fetch_daf.py --jour 2026-09-23        # collecte
python3 scripts/build_fiche.py --jour 2026-09-23      # les deux fiches + PDF
python3 scripts/whatsapp.py --jour 2026-09-23 --out messages/2026-09-23.txt
python3 scripts/check.py audit|jalons|sources
python3 scripts/build_bavli.py                        # index, une fois
```

Aucune dépendance Python externe. Le PDF passe par Chrome ou Chromium, cherché
dans `$DAF_CHROME`, puis `/Applications`, puis le `PATH`. Le Markdown est
converti par `pandoc`.

## Trois pièges documentés

- **Les commentateurs** se récupèrent par l'API `links`, pas par
  `Rashi on <traité>.<daf>` qui ne renvoie que des fragments. Sur Bekhorot 5 :
  44 dibbourim de Rashi par `links`, contre 1 par la référence directe.
- **Chekalim** est étudié dans le Yerushalmi : l'API donne une plage de
  chapitres, pas un amoud.
- **Sefaria limite le débit.** Ne jamais balayer une plage de dates en
  interrogeant l'API pour chacune : le cycle avançant d'un daf par jour, une
  plage se calcule depuis un ancrage puis se recoupe sur quelques points.

Détail dans `references/`.

## Sources et attribution

Textes araméens et traduction anglaise : Sefaria. Notions de fond, variantes
textuelles et difficultés : Kollel Iyun Hadaf. Les traductions et exposés
français sont produits d'après ces sources ; ce ne sont pas des traductions
publiées, et chaque fiche le mentionne.
