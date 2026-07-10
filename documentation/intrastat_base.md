# Module `intrastat_base`

**Dépôt :** https://github.com/OCA/intrastat-extrastat (branche `18.0`)
**Auteur :** Akretion / ACSONE / Noviat / OCA
**Licence :** AGPL-3
**Dépendances :** `base_vat` (cf. [base_vat.md](./base_vat.md)), `account`
**Incompatible avec :** `account_intrastat` (`excludes`)

---

## Objectif

Module **socle technique** pour les déclarations Intrastat (échanges intracommunautaires de biens/services au sein de l'UE). Il ne produit pas de déclaration en lui-même : il fournit les champs et l'infrastructure communs, réutilisés par des modules pays/déclaration spécifiques comme `l10n_fr_intrastat_product` (DEB - Déclaration d'Échange de Biens), `l10n_fr_intrastat_service` (DES - Déclaration Européenne de Services), ou `l10n_be_intrastat_product` (Belgique).

## Pourquoi c'est une dépendance de `account_invoice_en16931`

La norme EN16931 (factures électroniques transfrontalières UE) a besoin de distinguer **biens vs services** et de connaître le régime fiscal applicable à la transaction pour certains champs de la facture — exactement les informations que ce module ajoute nativement.

## Ce que fait le code concrètement

- **`product.template`** : ajoute `intrastat_type` (calculé — `product` ou `service`, déduit du type de produit Odoo) et `is_accessory_cost` (frais accessoires : transport, emballage... rattachés à une vente de biens).
- **`account.move`** : ajoute `intrastat_fiscal_position` (calculé depuis la position fiscale du partenaire), pour savoir si la transaction entre dans le champ des déclarations Intrastat.

## Installation

Dépôt distinct des autres modules déjà documentés :

```bash
cd /tmp
git clone -b 18.0 --depth 1 https://github.com/OCA/intrastat-extrastat.git
mv intrastat-extrastat/intrastat_base /media/sf_dev_odoo/18.0/facturation-electronique/
rm -rf intrastat-extrastat
```

## Sources

- Module : https://github.com/OCA/intrastat-extrastat/tree/18.0/intrastat_base
- Dépendance technique : [base_vat.md](./base_vat.md)
- Module dépendant : [account_invoice_en16931.md](./account_invoice_en16931.md)
