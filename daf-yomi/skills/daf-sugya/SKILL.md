---
name: daf-sugya
description: Approfondit une sugya précise d'un daf — le fil de l'argument, Rashi et Tossafot sur le passage, les résolutions des A'haronim, les renvois vers d'autres traités. Déclencher sur « approfondis cette sugya », « que dit Rashi ici », « et Tossafot », « explique-moi ce passage », « la sugya de … », « d'où vient cette déduction ».
---

# Approfondir une sugya

Sert quand la fiche ne suffit pas : on veut le détail d'un passage, ce qu'en
disent les commentateurs, et où la discussion se poursuit ailleurs.

## 1. Le matériau est déjà là

La collecte (`fiches/<slug>.source.json`) contient :

- l'araméen segmenté et la traduction Davidson d'appui ;
- `commentateurs` : les dibbourim de **Rashi** et **Tossafot**, chacun avec son
  `ancre` — le segment du daf qu'il commente ;
- `insights` : les difficultés du Kollel, avec les sources nommées.

S'il manque, le produire :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/fetch_daf.py "Bekhorot 5"
```

## 2. Le point technique à ne pas oublier

Les commentateurs viennent de l'**API `links`**, pas de la référence directe
`Rashi on <traité>.<daf>` — celle-ci ne renvoie que des fragments. Sur
Bekhorot 5 : 44 dibbourim de Rashi et 11 de Tossafot par `links`, contre un
fragment et rien par la référence directe.

Si l'on cherche un commentateur absent de la collecte, l'API `links` en expose
bien d'autres par daf — Steinsaltz, Tzela'h, Meiri, Jastrow, dictionnaire du
Talmud. Les demander explicitement :

```python
sefaria.commentateurs("Bekhorot.5a", ("Rashi", "Tosafot", "Steinsaltz", "Meiri"))
```

## 3. Ce qu'on produit

En français, dans `fiches/<slug>.sugya-<n>.md` :

- **La question** : ce que la sugya cherche, et pourquoi c'est une question.
- **Le fil** : chaque mouvement de l'argument, en citant l'araméen par son
  segment — jamais de mémoire.
- **Rashi** : les dibbourim qui portent sur ce passage, traduits, avec leur
  ancre. Ne pas réinventer : les prendre dans la collecte.
- **Tossafot** : de même. Signaler s'il n'y en a aucun sur ce passage.
- **Les résolutions** : ce que les A'haronim en font, d'après les insights.
- **Où ça continue** : les renvois vers d'autres traités que donne le daf ou
  Tossafot.

## Limite à tenir

Ne jamais attribuer à Rashi ou à Tossafot un propos qui n'est pas dans la
collecte. Si un dibbour manque pour le passage étudié, le dire — c'est une
information, pas un trou à combler.
