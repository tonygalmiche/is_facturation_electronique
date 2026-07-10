# Module `base_vat`

**Éditeur :** Odoo SA (module **natif**, inclus dans Odoo Community — `odoo/addons/base_vat`)
**Licence :** LGPL-3
**Dépendances :** `account`

---

## Objectif

Module officiel Odoo (pas OCA, pas Akretion) : valide le format des numéros de TVA intracommunautaire saisis sur les partenaires (`res.partner.vat`). Le pays est déduit du préfixe à 2 lettres du numéro (ex. `BE0477472701` → règles belges).

Deux niveaux de validation :

- **Par défaut** : contrôle hors-ligne (règles de format/clé de contrôle propres à chaque pays), rapide, toujours disponible.
- **Option "VAT VIES Check"** (activable dans la config société) : vérification en ligne auprès de la base **VIES** de l'UE, qui confirme que le numéro est réellement attribué et actif. Plus lent, nécessite une connexion Internet, pas toujours disponible.

Pays couverts : ceux de l'UE, plus quelques pays hors UE (Chili, Colombie, Mexique, Norvège, Russie...). Pour les pays non supportés, seul le code pays est vérifié.

## Pourquoi c'est une dépendance ici

Utilisé par [account_invoice_en16931.md](./account_invoice_en16931.md) et par [l10n_fr_pdp.md](./l10n_fr_pdp.md) (méthode `check_vat()` appelée sur le partenaire pour valider son numéro de TVA avant transmission de la facture électronique — un numéro de TVA invalide fait échouer la validation EN16931/PDP).

## Installation

**Aucune action requise** : ce module fait partie du cœur d'Odoo Community, déjà présent dans toute installation standard (`odoo/addons/base_vat`). Il s'installe automatiquement comme dépendance des autres modules qui en ont besoin, pas besoin de le cloner depuis un dépôt externe.

## Sources

- Code source : https://github.com/odoo/odoo/tree/18.0/addons/base_vat
- Modules dépendants : [account_invoice_en16931.md](./account_invoice_en16931.md), [l10n_fr_pdp.md](./l10n_fr_pdp.md)
