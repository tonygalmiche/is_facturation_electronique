# Module `base_unece`

**Dépôt :** https://github.com/OCA/community-data-files (sous-module `base_unece`, branche `18.0`)
**Auteur :** Akretion France / OCA
**Licence :** LGPL-3
**Dépendances :** `base`

---

## Objectif

Module technique de base pour l'utilisation des listes de codes standardisées par l'**UNECE** (United Nations Economic Commission for Europe), aussi appelées **UNCL** (United Nations Code List). L'UNECE a standardisé des listes de codes pour de nombreux domaines : unités de mesure, moyens de paiement, modes de transport, emballages, **taxes**, etc.

C'est la **dépendance technique** de [account_tax_unece](./account_tax_unece.md) (codes de type/catégorie de taxe UNECE, utilisés par CII/UBL) — sans ce module, `account_tax_unece` ne peut pas s'installer :

> *"Vous essayez d'installer le module 'account_tax_unece' qui dépend du module 'base_unece'."*

Menu ajouté : **"UNECE Code Lists"**, sous *Réglages (mode développeur) > Technique > Paramètres* (menu parent `menu_ir_property`, "Parameters"/"Paramètres").

## C'est quoi concrètement, une liste UNECE ?

Ce sont des **nomenclatures standardisées** publiées par l'UNECE pour le commerce international et l'échange de documents électroniques (EDI, factures...). Le principe : au lieu que chaque système utilise du texte libre ("TVA", "Vat", "taxe sur la valeur ajoutée"...), tout le monde utilise le **même code standardisé**, ce qui permet un traitement automatisé fiable entre systèmes différents.

Elles sont regroupées sous le nom **UNCL** (United Nations Code List), chaque liste ayant un numéro. Dans le contexte de ce projet, les listes qui comptent :

- **UNCL 5153** — codes de **type de taxe** (ex. `VAT` pour la TVA)
- **UNCL 5305** — codes de **catégorie de taxe** (ex. `S` = taux standard, `E` = exonéré, `Z` = taux zéro, `AE` = autoliquidation...)
- et bientôt **VATEX** — codes de **motif d'exonération** (ex. `VATEX-EU-O`, `VATEX-FR-FRANCHISE`), ajoutés par la PR #277 sur [account_tax_unece](./account_tax_unece.md)

Ces codes sont directement intégrés dans le XML des factures électroniques **CII** et **UBL** (donc Factur-X aussi) — sans le bon code UNECE sur chaque taxe, la facture générée par Odoo ne sera pas conforme au schématron EN16931/Factur-X.

Il existe des dizaines d'autres listes UNECE pour d'autres domaines (unités de mesure, moyens de transport, emballages...), d'où le choix de `base_unece` d'avoir un seul modèle générique plutôt qu'un par liste (cf. section suivante).

## Ce que fait le code concrètement

Le module crée **un seul modèle Odoo générique**, `unece.code.list`, plutôt qu'un modèle par nomenclature. Raison donnée dans le code source (`models/unece_code_list.py`) : il existe des dizaines de listes UNECE différentes (taxes, unités de mesure, transport...) ; créer un modèle séparé pour chacune dupliquerait le code Python, les vues, les menus, les droits d'accès, etc.

Champs du modèle :

- `code` — le code (ex. `S`, `E`, `Z`...)
- `name` — le libellé
- `type` — un champ `Selection` **vide par défaut** (`fields.Selection([], ...)`), volontairement : chaque module dépendant vient y ajouter ses propres valeurs par héritage Python (`selection_add`). C'est le champ discriminant qui sert de "type de nomenclature".
- `description`
- contrainte SQL d'unicité sur `(type, code)`

Le module fournit aussi une vue liste/formulaire générique et le menu technique pour consulter toutes les nomenclatures, tous types confondus.

**En résumé** : `base_unece` ne contient aucune donnée en lui-même, seulement l'infrastructure (modèle + vues + menu). C'est `account_tax_unece` qui vient y injecter les vraies données (codes de type/catégorie de taxe UNECE, et bientôt les codes VATEX via la PR #277).

## Installation

Contrairement à `account_tax_unece`, ce module n'est pas concerné par la PR VATEX (#277) : la version officielle de la branche `18.0` d'OCA suffit. Même principe que pour `account_tax_unece` : clone temporaire dans `/tmp`, on ne garde que le dossier du module.

```bash
cd /tmp
git clone -b 18.0 --depth 1 https://github.com/OCA/community-data-files.git
mv community-data-files/base_unece /media/sf_dev_odoo/18.0/facturation-electronique/
rm -rf community-data-files
```

## Sources

- Dépôt officiel du module : https://github.com/OCA/community-data-files/tree/18.0/base_unece
- Module dépendant : [account_tax_unece.md](./account_tax_unece.md)
