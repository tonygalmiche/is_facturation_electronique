# Module `account_invoice_import`

**Auteur :** Akretion, Odoo Community Association (OCA)
**Version :** 18.0.1.1.0
**Licence :** AGPL-3
**Dépôt :** https://github.com/OCA/edi (branche 18.0)
**Dépendances :** `account`, `base_iban` (core Odoo), `base_business_document_import` (cf. [base_business_document_import.md](./base_business_document_import.md))

---

## Objectif

Import de factures fournisseur (PDF ou XML) : assistant qui, à partir d'un fichier déposé, extrait les données de la facture et crée (ou complète) la facture fournisseur correspondante dans Odoo, en s'appuyant sur les méthodes de matching de `business.document.import`.

- Si le fichier est un **XML** (CII ou UBL), il est parsé directement.
- Si c'est un **PDF**, le module cherche d'abord un **XML embarqué** (cas Factur-X : XML attaché au PDF, extrait via `pypdf`) ; sans XML embarqué, il faut un module complémentaire type `account_invoice_import_invoice2data` (non installé ici) pour extraire les données par reconnaissance de gabarit — non nécessaire pour Super PDP, dont les PDF contiennent un XML embarqué.

Utilisé ici comme dépendance de [l10n_fr_einvoicing_import](./l10n_fr_einvoicing_import.md), qui l'appelle pour importer automatiquement les factures fournisseur reçues de Super PDP (flux de type `SupplierInvoice`).

---

## Installation

```bash
cd /tmp
git clone -b 18.0 --depth 1 --filter=blob:none --sparse https://github.com/OCA/edi.git
cd edi
git sparse-checkout set account_invoice_import
mv account_invoice_import /media/sf_dev_odoo/18.0/facturation-electronique/
cd /tmp && rm -rf edi
```

Dépendance déjà présente dans ce dépôt : [base_business_document_import.md](./base_business_document_import.md) (à récupérer avant si pas déjà fait). `base_iban` et `account` sont des modules core Odoo, déjà installés.
