# Module `l10n_fr_einvoicing_import`

**Auteur :** Akretion
**Version :** 18.0.1.0.0
**Licence :** AGPL-3
**Dépôt :** https://github.com/akretion/fr-einvoicing (branche 18.0)
**Dépendances :** [l10n_fr_einvoicing](./l10n_fr_einvoicing.md), [account_invoice_import](./account_invoice_import.md)

---

## Objectif

Implémente réellement la création des factures fournisseur importées depuis la plateforme (Super PDP), en s'appuyant sur le module OCA `account_invoice_import`.

`l10n_fr_einvoicing` définit une méthode `_import_supplier_invoice()` volontairement vide ([`fr_einvoicing_flow.py:551-556`](../../l10n_fr_einvoicing/models/fr_einvoicing_flow.py#L551-L556)) — un point d'extension, avec ce commentaire explicite dans le code :

> *"Method inherited in l10n_fr_einvoicing_import. If you don't want to use the OCA module account_invoice_import, you can develop an alternative to l10n_fr_einvoicing_import and inherit this method"*

`l10n_fr_einvoicing_import` la surcharge pour appeler `account.invoice.import.create_invoice_webservice()` sur le fichier reçu (PDF avec XML Factur-X embarqué, ou XML seul) et créer la facture fournisseur.

**Sans ce module installé**, `_import_supplier_invoice()` renvoie toujours `False` : aucune exception, mais aucune facture créée non plus — Odoo journalise juste "Odoo failed to create the supplier invoice/refund" (cf. [import-depuis-super-pdp.md](./import-depuis-super-pdp.md)). En cascade, les événements de cycle de vie suivants (`SupplierInvoiceLC`) échouent aussi puisqu'ils cherchent une facture qui n'a jamais été créée.

---

## Installation

Vit dans le même dépôt `akretion/fr-einvoicing` que [l10n_fr_einvoicing](./l10n_fr_einvoicing.md#installation) : même clone temporaire, ne garder que ce dossier.

```bash
cd /tmp
git clone -b 18.0 --depth 1 https://github.com/akretion/fr-einvoicing.git
mv fr-einvoicing/l10n_fr_einvoicing_import /media/sf_dev_odoo/18.0/facturation-electronique/
rm -rf fr-einvoicing
```

Dépendance à installer au préalable : [account_invoice_import.md](./account_invoice_import.md) (et sa propre dépendance [base_business_document_import.md](./base_business_document_import.md)).
