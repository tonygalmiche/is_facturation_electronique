# Module `l10n_fr_account`

**Éditeur :** Odoo SA (module **natif**, inclus dans Odoo Community — `odoo/addons/l10n_fr_account`)
**Nom complet :** France - Accounting
**Licence :** LGPL-3
**Dépendances :** `base_iban`, `base_vat` (cf. [base_vat.md](./base_vat.md)), `account`, `l10n_fr`
**Auto-installé** avec `account` pour les sociétés basées en France métropolitaine (pas les DOM-TOM)

---

## Objectif

C'est la **localisation comptable française standard d'Odoo** (plan comptable, taxes TVA, export FEC...) — pas un module spécifique à la réforme e-invoicing. Elle s'applique aux sociétés basées en France métropolitaine (ne gère pas correctement les DOM-TOM : Guadeloupe, Martinique, Guyane, Réunion, Mayotte, cf. limitation documentée dans le module lui-même).

Contenu principal :

- Plan comptable français (`data/account_chart_template_data.xml`)
- Taxes TVA françaises, y compris les taxes "TTC" pour les achats (utile notamment pour le module `hr_expense`) — ces taxes TTC ne sont pas gérées par les positions fiscales du module
- Rapport de taxes (tax report / déclaration de TVA)
- Assistant d'export **FEC** (Fichier des Écritures Comptables, obligation légale française)

## Pourquoi c'est une dépendance ici

C'est une dépendance de [l10n_fr_pdp.md](./l10n_fr_pdp.md) (le module officiel Odoo de facturation électronique) — logique, la réforme s'appuie sur la comptabilité française standard déjà en place (plan comptable, taxes) plutôt que de la redéfinir.

## Installation

**Aucune action requise** : module natif d'Odoo Community, déjà présent dans toute installation standard. S'auto-installe automatiquement dès que `account` est installé sur une société dont le pays fiscal est la France métropolitaine.

## Sources

- Code source : https://github.com/odoo/odoo/tree/18.0/addons/l10n_fr_account
- Documentation officielle : https://www.odoo.com/documentation/18.0/applications/finance/fiscal_localizations/france.html
- Module dépendant : [l10n_fr_pdp.md](./l10n_fr_pdp.md)
