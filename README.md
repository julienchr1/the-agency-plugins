# the-agency-plugins

Place de marché de plugins Claude développés par **The Agency**.

## Installation

### Claude (compte) — pour Cowork et claude.ai

Paramètres → **Personnaliser → Plugins → Ajouter → Ajouter depuis un dépôt**,
puis coller :

```
julienchr1/the-agency-plugins
```

Les plugins installés depuis une place de marché se mettent à jour depuis ce
dépôt.

### Claude Code (local)

```bash
claude plugin marketplace add julienchr1/the-agency-plugins
claude plugin install michna-yomit@the-agency
```

## Plugins

### michna-yomit

Étude quotidienne de la Michna, entièrement sourcée sur
[Sefaria](https://www.sefaria.org), avec les notions de fond de
[dafyomi.co.il](https://www.dafyomi.co.il) en complément.

Pour chaque michna : texte hébreu intégral, traduction française, explication,
**la totalité des sections du Bartenura** en hébreu avec leur traduction
française, renvois au Talmud — en Markdown, HTML et PDF.

Sept skills : la journée complète, la fiche d'une michna, le calendrier du
programme (63 traités, 4192 michnaiot), le message WhatsApp quotidien, les
jalons de traité (ouverture, siyoum), les sujets de Guemara, et un monitoring
hebdomadaire.

Voir [`michna-yomit/README.md`](michna-yomit/README.md).

## Structure d'une place de marché

```
.claude-plugin/marketplace.json     la liste des plugins
<nom-du-plugin>/
  .claude-plugin/plugin.json        le manifeste du plugin
  skills/<skill>/SKILL.md
  scripts/ data/ references/
```

## Licence et sources

Le code des plugins est publié tel quel, sans garantie.

`michna-yomit` reproduit des textes provenant de Sefaria (domaine public ou
CC-BY-NC selon la version — chaque fiche porte ses liens de source) et renvoie
vers les pages du Kollel Iyun Hadaf (dafyomi.co.il). Les traductions
françaises sont produites par Claude d'après ces sources ; ce ne sont pas des
traductions publiées.
