# API Sefaria — ce qui est utilisé, et les pièges

Vérifié le 23 septembre 2026. Base : `https://www.sefaria.org/api`. Aucune clé.

## Le calendrier — la position du jour

```
GET /calendars?year=2026&month=9&day=23
```

Dans `calendar_items`, l'entrée dont `title.en == "Daf Yomi"` porte :

- `displayValue.en` — le libellé affiché, ex. `Bekhorot 5`
- `ref` — **la référence exacte**, qui fait foi

Fonctionne sur les dates passées et futures. **Il n'y a donc aucun calendrier à
calculer.** Hors du cycle connu, l'entrée est absente : c'est ainsi qu'on
trouve la fin de cycle, par bissection.

### Le piège Chekalim

Le cycle Daf Yomi étudie Chekalim dans le **Yerushalmi**. Pour ces jours, `ref`
ne vaut pas un amoud mais une plage de chapitres :

```
displayValue = "Shekalim 11"
ref          = "Jerusalem Talmud Shekalim 4:2:15-3:3"
```

Toujours utiliser `ref`, jamais reconstruire depuis le libellé.

## Le texte d'un amoud

```
GET /texts/Bekhorot.5a?context=0&commentary=0
```

- `he` → araméen segmenté
- `text` → traduction anglaise (William Davidson), explicative

Un daf fait typiquement 5 000 à 10 000 caractères d'araméen sur les deux amudim.

## Les commentateurs — le piège principal

**Ne pas utiliser `GET /texts/Rashi_on_<traité>.<daf>`** : cette référence ne
renvoie que des fragments.

```
GET /links/Bekhorot.5a?with_text=1
```

Filtrer sur `collectiveTitle.en`. Chaque lien porte `anchorRef`, le segment du
daf qu'il commente.

Mesure sur Bekhorot 5 :

| | référence directe | API `links` |
|---|---|---|
| Rashi | 1 fragment, 42 car. | **44 dibbourim, 4 468 car.** |
| Tossafot | absent | **11 dibbourim, 3 629 car.** |

L'API `links` expose par daf bien d'autres commentateurs : Steinsaltz, Tzela'h,
Meiri, Jastrow, dictionnaire du Talmud.

## La structure d'un traité

```
GET /shape/Bekhorot
```

`length` = nombre d'amudim, **indexés depuis 1a** (folio 1, vide). Le dernier
daf vaut donc `ceil(length / 2)` — et non `1 + length // 2`. Vérifié traité par
traité : 37 valeurs sur 38 concordent avec les nombres connus, Chekalim étant
un cas à part.

## Limitation de débit

Sefaria répond **HTTP 429** si on l'interroge en rafale. Le client impose un
intervalle minimum de 0,35 s entre deux appels réseau et un backoff quadratique
sur 429. Surtout : **ne jamais balayer une plage de dates en interrogeant l'API
pour chacune.** Le cycle avançant d'un daf par jour sans saut, une plage se
calcule depuis un seul ancrage (`daf_calendar.sequence`), puis se recoupe avec
l'API sur deux ou trois points.
