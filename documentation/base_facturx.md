# Module `base_facturx`

**Auteur :** Akretion, Odoo Community Association (OCA)
**Version :** 18.0.1.0.0
**Licence :** AGPL-3
**Dépôt :** https://github.com/OCA/edi (branche 18.0)
**Dépendances :** `uom_unece`, `account_tax_unece`, `account_payment_unece` (déjà présents dans ce dépôt)

---

## Objectif

Module technique (pas de fonctionnalité autonome) fournissant les bases communes (mapping des codes UNECE ↔ champs Odoo) utilisées par [`account_invoice_import_facturx`](./account_invoice_import_facturx.md) pour parser le XML CII/Factur-X.

## Installation

```bash
cd /tmp
git clone -b 18.0 --depth 1 --filter=blob:none --sparse https://github.com/OCA/edi.git
cd edi
git sparse-checkout set base_facturx
mv base_facturx /media/sf_dev_odoo/18.0/facturation-electronique/
cd /tmp && rm -rf edi
```

Dépendances déjà présentes dans ce dépôt : [uom_unece.md](./uom_unece.md), [account_tax_unece.md](./account_tax_unece.md), [account_payment_unece.md](./account_payment_unece.md).
