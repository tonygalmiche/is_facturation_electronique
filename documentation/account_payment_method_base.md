# Module `account_payment_method_base`

**Dépôt :** https://github.com/OCA/account-payment (sous-module `account_payment_method_base`, branche `18.0`)
**Auteur :** Akretion France / OCA
**Licence :** AGPL-3
**Statut :** Mature
**Dépendances :** `account`

---

## Objectif

Petit module technique : le modèle natif **`account.payment.method`** est défini dans le module `account` d'Odoo, mais celui-ci ne fournit **aucune vue** pour ce modèle (ni liste, ni formulaire, ni menu). `account_payment_method_base` comble ce manque en ajoutant les vues manquantes.

C'est une dépendance de [account_payment_unece.md](./account_payment_unece.md), qui a besoin de vues fonctionnelles sur `account.payment.method` pour y afficher le nouveau champ de code UNECE.

## Ce que fait le code concrètement

Sur le modèle `account.payment.method`, ajoute :

- `line_ids` — champ `One2many` vers `account.payment.method.line`, absent nativement du module `account`
- un tri par défaut (`code, payment_type`)
- un `display_name` calculé plus lisible, au format `[code] Nom (Type de paiement)`

Côté données : une vue liste, une vue formulaire et une entrée de menu pour ce modèle (rien d'autre — pas de nouveau champ métier, juste l'infrastructure d'affichage).

## Installation

Dépôt distinct de `community-data-files` (attention, pas le même repo que les modules `*_unece`) :

```bash
cd /tmp
git clone -b 18.0 --depth 1 https://github.com/OCA/account-payment.git
mv account-payment/account_payment_method_base /media/sf_dev_odoo/18.0/facturation-electronique/
rm -rf account-payment
```

## Sources

- Module : https://github.com/OCA/account-payment/tree/18.0/account_payment_method_base
- Module dépendant : [account_payment_unece.md](./account_payment_unece.md)
