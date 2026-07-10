# Module `account_invoice_en16931`

**Auteur :** Akretion France
**Version :** 18.0.1.0.0
**Licence :** AGPL-3
**Dépôt :** https://github.com/akretion/fr-einvoicing (branche 18.0)
**Dépendances Odoo :** `account_tax_unece`, `uom_unece`, `account_payment_unece`, `base_vat`, `intrastat_base`
**Dépendance Python :** `factur-x>=6.1` (cf. [lib-factur-x.md](./lib-factur-x.md))
**Incompatible avec :** `account_einvoice_generate` (`excludes`)

---

## Objectif

Module **générique** (pas spécifique à la France) de génération de factures électroniques conformes à la norme européenne **EN16931**. C'est la ré-écriture complète évoquée dans [akretion.md](./akretion.md), qui remplace l'ancien module OCA `account_invoice_facturx`. Il gère à la fois **Factur-X** et **UBL** — un seul moteur de génération XML, partagé entre les deux formats (le choix entre les deux se fait au niveau de la lib `factur-x`).

Module parent dans la chaîne de dépendances :

```
l10n_fr_einvoicing → l10n_fr_account_invoice_en16931 → account_invoice_en16931
```

(cf. [l10n_fr_account_invoice_en16931.md](./l10n_fr_account_invoice_en16931.md) pour la surcouche France).

## Ce que fait le code concrètement

### Génération du XML (`models/account_move.py`)

Le cœur du module : une série de méthodes `_prepare_btXX`/`_prepare_bgXX` (une par bloc/tag de la norme EN16931 — BT = Business Term, BG = Business Group) qui construisent un dictionnaire de données, assemblé par `_prepare_en16931_dict` puis transformé en XML Factur-X par `generate_facturx_xml()` via la lib `factur-x`.

`generate_facturx_xml()` détermine aussi **quel schématron appliquer** selon le contexte (variable `check_schematron`) :

- `base` — schématron Factur-X standard
- `fr-ctc` — schématron Factur-X + schématron de la réforme française
- `fr-chorus` — schématron additionnel Chorus Pro (pas encore disponible, cf. [documentation-pyfrctc.md](./documentation-pyfrctc.md))

### Paramètres Saxon Server (`wizards/res_config_settings.py`)

**C'est ce module qui expose les deux paramètres Saxon Server** documentés dans [saxon-server.md](./saxon-server.md), sur la page de configuration de la compta :

```python
saxon_server_url = fields.Char(config_parameter="en16931.saxon_server_url")
saxon_server_codedb_dir = fields.Char(config_parameter="en16931.saxon_server_codedb_dir")
```

Noms techniques exacts des `ir.config_parameter` : **`en16931.saxon_server_url`** et **`en16931.saxon_server_codedb_dir`**. Récupérés par `_get_specific_saxon_server_url()` / `_get_saxon_server_codedb_dir()` avant chaque appel à `generate_facturx_xml()`.

### Vérification de config (`models/res_company.py`, méthode `_en16931_checks`)

C'est le code derrière le bouton **"Check config for EN16931 invoicing"** (cf. [akretion.md](./akretion.md)) :

- Vérifie que chaque taxe de vente a un code d'exonération VATEX valide (`_en16931_check_sale_tax`) — **dépend directement de la PR VATEX #277** sur [account_tax_unece.md](./account_tax_unece.md) (le champ `no_vat_taxes_vatex_id` filtre sur `unece.code.list` avec `type = "tax_vatex"`, qui n'existe que grâce à cette PR).
- Vérifie la précision décimale du prix produit (max 4 décimales pour EN16931, règle issue de la norme AFNOR XP Z12-012).
- Vérifie la précision décimale de l'unité de mesure produit (max 4 décimales).

Champ `no_vat_taxes` (calculé) : vrai si la société n'a aucune taxe de type `VAT` — utile pour les entités non assujetties (auto-entrepreneurs, associations), qui doivent alors renseigner `no_vat_taxes_vatex_id` (motif d'exonération global de la société).

## Installation

Ce module vit dans le même dépôt `akretion/fr-einvoicing` que `l10n_fr_account_invoice_en16931` (sa dépendance directe côté France) : même clone, mêmes commandes — cf. [l10n_fr_account_invoice_en16931.md](./l10n_fr_account_invoice_en16931.md#installation). Ne pas oublier la dépendance Python `factur-x>=6.1` (cf. [lib-factur-x.md](./lib-factur-x.md)), sans laquelle l'installation du module échoue.

## Sources

- Module : https://github.com/akretion/fr-einvoicing/tree/18.0/account_invoice_en16931
- Contexte de la réécriture : [akretion.md](./akretion.md)
- Module France : [l10n_fr_account_invoice_en16931.md](./l10n_fr_account_invoice_en16931.md)
- Configuration Saxon Server détaillée : [saxon-server.md](./saxon-server.md)
- Lib Python requise : [lib-factur-x.md](./lib-factur-x.md)
- Dépendance VATEX : [account_tax_unece.md](./account_tax_unece.md), [base_unece.md](./base_unece.md)
