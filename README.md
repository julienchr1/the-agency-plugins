# the-agency-plugins

Place de marché de plugins Claude développés par **The Agency**.

## Installation

### Claude (compte) — pour Cowork et claude.ai

Paramètres → **Personnaliser → Plugins → Ajouter → Ajouter depuis un dépôt**,
puis coller :

```
julienchr1/the-agency-plugins
```

### Comment les mises à jour se propagent

La synchronisation automatique **ne se déclenche pas sur un push direct**. Le
centre d'aide Claude est explicite :

> *Once enabled, automatic sync runs when a pull request that includes a plugin
> version bump is merged to the repository's default branch.*
> *Direct pushes to the default branch don't trigger a sync.*
> *Syncs can take up to 30 minutes depending on the number of plugins.*

Le workflow à suivre pour publier une modification est donc :

1. une branche ;
2. un **bump de `version`** dans `<plugin>/.claude-plugin/plugin.json` ;
3. une pull request ;
4. une fusion sur `main`.

Le bump de version n'est pas cosmétique : côté compte la synchro le réclame
comme déclencheur, et côté CLI local `claude plugin update` compare ce champ —
à version identique il ne recopie rien.

En cas de doute, le refresh manuel reste fiable (~20 s) :
*Plugins → Ajouter → Gérer les marketplaces → ⋯ → Rechercher des mises à jour*.

Référence : <https://support.claude.com/en/articles/13837433-manage-plugins-for-your-organization>
(rédigé pour les organisations ; même interface pour un compte personnel).

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
