# Module `base_business_document_import`

**Auteur :** Akretion, Nicolas JEUDY, Odoo Community Association (OCA)
**Version :** 18.0.2.0.1
**Licence :** AGPL-3
**Dépôt :** https://github.com/OCA/edi (branche 18.0)
**Dépendances :** `account_tax_unece`, `uom_unece` (déjà présents dans ce dépôt, cf. [account_tax_unece.md](./account_tax_unece.md), [uom_unece.md](./uom_unece.md))

---

## Objectif

Module technique (pas de fonctionnalité autonome, pas de menu) fournissant le modèle abstrait **`business.document.import`** : une boîte à outils de méthodes de *matching* pour retrouver dans Odoo les enregistrements correspondant aux données brutes d'un document externe (facture, commande) importé au format PDF/XML/CSV.

Sert de socle à des modules OCA plus haut niveau non installés ici (`account_invoice_import`, `sale_invoice_import`), mais est utilisé directement par [`l10n_fr_einvoicing`](./l10n_fr_einvoicing.md) pour retrouver le partenaire fournisseur à partir du SIREN/SIRET reçu dans les événements Super PDP (`_match_partner_from_event`, [fr_einvoicing_flow.py:711](../../l10n_fr_einvoicing/models/fr_einvoicing_flow.py#L711)).

---

## Modèle `business.document.import` (AbstractModel — aucune table créée)

Principales méthodes de matching :

| Méthode | Rôle |
|---------|------|
| `_match_partner` | Orchestrateur principal : essaie successivement référence, contact (email/nom/tél.), nom, site web |
| `_match_partner_ref` | Match par référence externe explicite |
| `_match_partner_contact` | Match par email, nom de contact ou téléphone |
| `_match_partner_name` | Match par nom (recherche insensible à la casse) |
| `_match_partner_website` / `_match_partner_email` | Match par domaine de site web / email |
| `_hook_match_partner` | Point d'extension pour logique de matching personnalisée |
| `_match_shipping_partner` | Match de l'adresse de livraison |
| `_match_partner_bank` | Match ou création d'un compte bancaire partenaire (validation IBAN) |
| `_match_product` / `_match_product_search` | Match produit par ID, code-barres, référence ou info fournisseur |
| `_match_currency` | Match devise par code ISO, symbole ou pays |
| `_match_uom` | Match unité de mesure par code UNECE ou nom |
| `_match_taxes` / `_match_tax` | Match taxes (liste ou unitaire) |
| `_match_account` | Match compte comptable par code |
| `_match_analytic_account` | Match compte analytique par code |
| `_match_journal` | Match journal comptable par code |
| `_match_incoterm` | Match incoterm par code ou nom |
| `_check_company` | Valide le numéro de TVA du document contre la société courante |
| `_direct_match` | Match générique par recordset, ID ou XMLID |
| `compare_lines` | Compare lignes existantes et lignes importées (mise à jour/ajout) |
| `post_create_or_update` | Attache le fichier source, poste un message, journalise les avertissements d'import |

---

## Installation

```bash
cd /tmp
git clone -b 18.0 --depth 1 --filter=blob:none --sparse https://github.com/OCA/edi.git
cd edi
git sparse-checkout set base_business_document_import
mv base_business_document_import /media/sf_dev_odoo/18.0/facturation-electronique/
cd /tmp && rm -rf edi
```

Dépendances déjà présentes dans ce dépôt : [account_tax_unece.md](./account_tax_unece.md), [uom_unece.md](./uom_unece.md) — rien à cloner en plus.

---

## Erreur `KeyError: 'business.document.import'` à l'import des factures Super PDP

### Symptôme

Bouton "Import" (récupération des factures depuis Super PDP) :

```
File ".../l10n_fr_einvoicing/models/res_company.py", line 421, in _fr_ctc_run_import
    flow._process(result)
  File ".../l10n_fr_einvoicing/models/fr_einvoicing_flow.py", line 649, in _process
    move = self._match_invoice_from_event(event_dict, result)
  File ".../l10n_fr_einvoicing/models/fr_einvoicing_flow.py", line 686, in _match_invoice_from_event
    partner = self._match_partner_from_event(event_dict, result)
  File ".../l10n_fr_einvoicing/models/fr_einvoicing_flow.py", line 711, in _match_partner_from_event
    partner = self.env["business.document.import"]._match_partner(
KeyError: 'business.document.import'
```

### Cause

[`fr_einvoicing_flow.py:711`](../../l10n_fr_einvoicing/models/fr_einvoicing_flow.py#L711) appelle `self.env["business.document.import"]._match_partner(...)` pour retrouver le partenaire fournisseur à partir du SIREN/SIRET reçu dans l'événement Super PDP. Ce modèle est défini par le module OCA **`base_business_document_import`** (dépôt [OCA/edi](https://github.com/OCA/edi/tree/18.0), branche 18.0).

Or ce module :
- n'est **pas déclaré** dans `depends` du [`__manifest__.py`](../../l10n_fr_einvoicing/__manifest__.py) de `l10n_fr_einvoicing` (seulement `l10n_fr_siret_account` et `l10n_fr_account_invoice_en16931`)
- n'est **pas présent** dans l'arborescence locale des addons 18.0

→ le modèle n'existe pas dans le registry Odoo, d'où le `KeyError`.

### Correctif

1. Récupérer `base_business_document_import` (branche 18.0, dépôt `OCA/edi`) :

```bash
cd /tmp
git clone -b 18.0 --depth 1 --filter=blob:none --sparse https://github.com/OCA/edi.git
cd edi
git sparse-checkout set base_business_document_import
mv base_business_document_import /media/sf_dev_odoo/18.0/facturation-electronique/
cd /tmp && rm -rf edi
```

2. Ajouter la dépendance dans `l10n_fr_einvoicing/__manifest__.py` :

```python
"depends": [
    "l10n_fr_siret_account",
    "l10n_fr_account_invoice_en16931",
    "base_business_document_import",
],
```

3. Mettre à jour la liste des apps (`-u base_business_document_import,l10n_fr_einvoicing` ou bouton "Mettre à jour les listes d'applications" + installation manuelle du nouveau module), puis relancer l'import.

**Non fait à ce jour** : ce correctif n'a pas encore été appliqué dans ce dépôt (le manifest de `l10n_fr_einvoicing` ne liste toujours pas `base_business_document_import` et le module n'est pas cloné en local) — à faire avant de retester l'import Super PDP.
