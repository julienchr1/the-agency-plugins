# fiches/

Ce dossier contient des **échantillons** montrant le format attendu, pas le
dossier de travail. Les fiches réelles sont écrites dans le dossier de travail
(voir « Dossier de travail » dans le README du plugin).

Pour chaque michna, trois fichiers :

| fichier | produit par | contenu |
|---|---|---|
| `<ref>.source.json` | `fetch_mishna.py` | le matériel Sefaria brut |
| `<ref>.fr.json` | **Claude** | traduction, explication, Bartenura en français |
| `<ref>.md` | `build_fiche.py` | la fiche assemblée |

`build_fiche.py` produit aussi `.html` et `.pdf`, non conservés ici pour ne pas
alourdir le plugin.

Les échantillons portent sur Ohalot 2:4 et 2:5 : deux michnaiot consécutives,
qui montrent le format sur un cas réel (6 et 4 sections de Bartenura). Ce n'est
pas une journée du programme — le 17 septembre 2026 correspond à Ohalot 2:5-6.
