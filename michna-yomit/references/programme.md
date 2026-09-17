# Le programme

## Définition

| | |
|---|---|
| Départ | **16 juillet 2025**, Zeva'him 1:1 |
| Rythme | 2 michnaiot par jour |
| Jours | tous les jours, Chabbat inclus |
| Ordre | ordre canonique du Shas, en bouclant depuis Zeva'him |
| Étendue | 63 traités, 4192 michnaiot |
| Durée | 2096 jours — fin prévue le **11 avril 2031** |

L'ordre du cycle est donc : Kodachim (depuis Zeva'him) → Taharot → Zeraïm →
Moëd → Nachim → Nezikin.

Le 16 juillet 2025 était un **mercredi**. Le programme avait d'abord été
décrit comme démarrant « le mardi 16 juillet » : c'est le 16 juillet 2025 qui
a été retenu, pas le mardi 15.

## Ce programme n'est pas le cycle Mishnah Yomi de dafyomi.co.il

Le Dafyomi Advancement Forum publie un cycle « Mishnah Yomi » au même rythme de
2 michnaiot par jour, entré dans Zeva'him à la même période :

<https://www.dafyomi.co.il/calendars/myomi/todays_mishnah.php>

Il en est proche, mais **décalé d'une michna**. Le 17 septembre 2026, ce
programme était à **Ohalot 2:5-6** quand le cycle officiel était à
Ohalot 2:4-5.

C'est un repère utile pour comprendre un écart — **jamais** une référence pour
recaler le calendrier.

## La calibration

`data/program.json` porte `offset_mishnayot` et un bloc `calibration` qui
conserve une observation datée : *à telle date, la première des deux michnaiot
était celle-ci*. Chaque `build` revérifie cette observation.

**Cette observation vient de l'utilisateur, pas d'un site.** Le calcul brut
depuis le 16 juillet 2025 tombe juste : `offset_mishnayot = 0`.

Une erreur a été commise le 17/09/2026 : le calendrier avait été calibré sur le
cycle de dafyomi.co.il, ce qui l'avait décalé d'une michna (Ohalot 2:4-5 au lieu
de 2:5-6). Corrigé le jour même sur signalement de l'utilisateur. La règle qui
en découle : **si l'utilisateur signale un écart, sa position est juste par
définition.**

Un vrai écart de découpage entre éditions peut apparaître plus loin dans le
Shas. Dans ce cas, `calendar_build.py calibrate <date> "<ref>"` recale
l'ensemble — toujours sur une observation de l'utilisateur.

## Position au 17 septembre 2026

- jour **429** sur 2096
- **Ohalot 2:5-6**
- 856 michnaiot faites sur 4192 — **20,4 %**
- Kodachim achevé (Zeva'him → Kinim), Kelim achevé (254 michnaiot)
- Ohalot en cours : 12 faites sur 134, du 11/09/2026 au **16/11/2026** (67 jours)
- puis Negaïm (115 michnaiot) à partir du 17/11/2026
