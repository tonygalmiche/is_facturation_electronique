# Module `account_tax_unece`

**Dépôt :** https://github.com/OCA/community-data-files (sous-module `account_tax_unece`)
**Auteur :** Akretion France / OCA
**Licence :** LGPL-3
**Dépendances :** `account`, `base_unece`

---

## Objectif

Ajoute deux champs sur les taxes (`account.tax`) — **UNECE Type Code** et **UNECE Category Code** — pour permettre l'utilisation des nomenclatures de l'**UNECE** (United Nations Economic Commission for Europe) :

- le code de type de taxe UNECE est défini dans le [DataElement 5153](http://www.unece.org/trade/untdid/d97b/uncl/uncl5153.htm) ;
- le code de catégorie de taxe UNECE est défini dans le [DataElement 5305](http://www.unece.org/trade/untdid/d97a/uncl/uncl5305.htm).

Cette codification (UNCL) est utilisée par les deux standards de facturation électronique internationaux **CII** (Cross Industry Invoice) et **UBL** (Universal Business Language) — donc directement utile pour la réforme française et les modules Factur-X/UBL (cf. [saxon-server.md](./saxon-server.md), [l10n_fr_einvoicing.md](./l10n_fr_einvoicing.md)).

## Pourquoi une version spécifique (PR non mergée)

D'après [akretion.md](./akretion.md), la génération Factur-X conforme EN16931 nécessite, pour les taxes TVA de catégorie **E** (exonérées), un **code motif d'exonération** (VATEX). Ce champ n'existe pas encore dans la version officielle publiée du module `account_tax_unece` : il est ajouté par la PR OCA toujours ouverte, non mergée à ce jour :

**PR #277** — https://github.com/OCA/community-data-files/pull/277 — *"[18.0][IMP] account_tax_unece: add VAT exemption reason codes (VATEX)"*

Contenu de la PR :

| Fichier | Changement |
|---|---|
| `data/unece_tax_vatex.xml` | Ajoute la liste des codes VATEX (807 lignes de données) |
| `models/account_tax.py` | Ajoute le champ/la logique de code motif d'exonération sur la taxe |
| `models/res_company.py`, `models/unece_code_list.py` | Ajustements mineurs |
| `views/account_tax.xml`, `views/unece_code_list.xml` | Affichage du nouveau champ dans les vues |

- Branche de la PR : `18-account_tax_unece-vatex`, hébergée sur le fork **akretion/community-data-files** (pas encore sur `OCA/community-data-files`).
- Base : branche `18.0`.

## Installation

Le dépôt `community-data-files` contient de nombreux autres modules non utiles ici. On ne garde que le module `account_tax_unece` : clone temporaire dans `/tmp`, puis déplacement du seul dossier utile dans `/media/sf_dev_odoo/18.0/facturation-electronique/` (aux côtés de `fr-einvoicing`, `l10n-france`, etc.), et nettoyage du clone temporaire.

```bash
cd /tmp
git clone -b 18-account_tax_unece-vatex https://github.com/akretion/community-data-files.git
mv community-data-files/account_tax_unece /media/sf_dev_odoo/18.0/facturation-electronique/
rm -rf community-data-files
```

**⚠️ À surveiller** : ce dossier `account_tax_unece` est une copie figée à la date du clone, plus liée à aucun dépôt git — pas de mises à jour automatiques. Une fois la PR mergée dans `OCA/community-data-files` (branche `18.0`), refaire la même opération (clone temporaire + déplacement) depuis le dépôt officiel pour repartir sur une version à jour et suivie. Vérifier périodiquement le statut de la PR : https://github.com/OCA/community-data-files/pull/277

## Sources

- Dépôt officiel du module : https://github.com/OCA/community-data-files/tree/18.0/account_tax_unece
- PR à suivre : https://github.com/OCA/community-data-files/pull/277
- Contexte complet (discussion Alexis de Lattre) : [akretion.md](./akretion.md)
