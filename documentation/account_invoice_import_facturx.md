# Module `account_invoice_import_facturx`

**Auteur :** Akretion, Odoo Community Association (OCA)
**Version :** 18.0.1.1.0
**Licence :** AGPL-3
**Dépôt :** https://github.com/OCA/edi (branche 18.0)
**Dépendances Odoo :** [account_invoice_import](./account_invoice_import.md), [base_facturx](./base_facturx.md)
**Dépendance Python :** `factur-x` (déjà installée, cf. [lib-factur-x.md](./lib-factur-x.md))

---

## Objectif

Implémente réellement `parse_xml_invoice()` pour [account_invoice_import](./account_invoice_import.md), qui n'est sinon qu'un stub retournant `False` (point d'extension par format). C'est ce module qui sait parser le XML **CII** (Cross-Industry Invoice) embarqué dans un PDF Factur-X/ZUGFeRD et construire le dict `parsed_inv` (partenaire, lignes, montants, taxes...) attendu par le reste de la chaîne d'import.

**Sans ce module**, `parse_xml_invoice()` renvoie toujours `False`, et `parse_pdf_invoice()` (dans `account_invoice_import`) retombe alors sur un dict `parsed_inv = {}` **vide mais pas `False`** (donc pas d'erreur explicite à ce stade) — le code suivant (`_pre_process_parsed_inv`) accède directement à `parsed_inv["partner"]` sans `.get()`, d'où un `KeyError: 'partner'` sec à l'exécution. Cf. [import-depuis-super-pdp.md](./import-depuis-super-pdp.md#4-keyerror-partner--module-account_invoice_import_facturx-manquant) pour le détail de l'incident.

---

## Installation

```bash
cd /tmp
git clone -b 18.0 --depth 1 --filter=blob:none --sparse https://github.com/OCA/edi.git
cd edi
git sparse-checkout set account_invoice_import_facturx
mv account_invoice_import_facturx /media/sf_dev_odoo/18.0/facturation-electronique/
cd /tmp && rm -rf edi
```

Dépendances à installer au préalable : [account_invoice_import.md](./account_invoice_import.md), [base_facturx.md](./base_facturx.md).
