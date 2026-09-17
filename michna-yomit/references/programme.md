# Le programme

## Définition

| | |
|---|---|
| Départ | **16 juillet 2025**, Zeva'him 1:1 |
| Rythme | 2 michnaiot par jour |
| Jours | tous les jours, Chabbat inclus |
| Ordre | ordre canonique du Shas, en bouclant depuis Zeva'him |
| Étendue | 63 traités, 4192 michnaiot |
| Durée | 2097 jours — fin prévue le **12 avril 2031** |

L'ordre du cycle est donc : Kodachim (depuis Zeva'him) → Taharot → Zeraïm →
Moëd → Nachim → Nezikin.

Le 16 juillet 2025 était un **mercredi**. Le programme avait d'abord été
décrit comme démarrant « le mardi 16 juillet » : c'est le 16 juillet 2025 qui
a été retenu, pas le mardi 15.

## Rapport au 16ᵉ cycle Mishnah Yomi

Ce programme est aligné sur le **16ᵉ cycle Mishnah Yomi** du Dafyomi
Advancement Forum, qui est entré dans Zeva'him à la même période et publie le
même rythme de 2 michnaiot par jour :

<https://www.dafyomi.co.il/calendars/myomi/todays_mishnah.php>

C'est la référence à consulter en cas de doute sur la position réelle.

## Le décalage d'une michna

Les éditions ne découpent pas les michnaiot de façon identique. Entre
Zeva'him 1:1 et Ohalot 2, Sefaria en compte **une de plus** que l'édition
suivie par dafyomi.co.il.

Sans correction, le calcul depuis le 16 juillet 2025 donnait Ohalot 2:5-6 pour
le 17 septembre 2026, alors que le cycle officiel donnait Ohalot 2:4-5.

`data/program.json` porte donc `offset_mishnayot: -1`, calibré sur cette
observation. Le calendrier ainsi calibré reproduit exactement la semaine
publiée par le site :

| date | calendrier | site officiel |
|---|---|---|
| jeu. 17/09/2026 | Ohalot 2:4-5 | Ohalos 2:4-5 |
| ven. 18/09/2026 | Ohalot 2:6-7 | Ohalos 2:6-7 |
| sam. 19/09/2026 | Ohalot 3:1-2 | Ohalos 3:1-2 |
| dim. 20/09/2026 | Ohalot 3:3-4 | Ohalos 3:3-4 |

D'autres écarts de découpage peuvent apparaître plus loin dans le Shas. La
commande `calibrate` existe pour cela : elle recale l'ensemble sur une
observation réelle. Chaque `build` revérifie la calibration et prévient en cas
d'écart.

## Position au 17 septembre 2026

- jour **429** sur 2097
- **Ohalot 2:4-5**
- 856 michnaiot faites sur 4192 — **20,4 %**
- Kodachim achevé ; Taharot en cours (Kelim fait, Ohalot jusqu'au 17/11/2026)
