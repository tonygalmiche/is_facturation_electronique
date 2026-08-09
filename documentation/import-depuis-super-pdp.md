## Import des factures depuis Super PDP

### 1. `KeyError: 'business.document.import'`

`fr_einvoicing_flow.py:711` appelle `self.env["business.document.import"]._match_partner(...)`, modèle fourni par le module OCA [`base_business_document_import`](./base_business_document_import.md) — absent du manifest de `l10n_fr_einvoicing` et non installé. Corrigé en ajoutant `base_business_document_import` aux `depends` de `is_facturation_electronique` (cf. fiche module pour l'installation).

### 2. Le partenaire n'est jamais trouvé par SIREN

Une fois le module installé, l'import échoue quand même :

```
WARNING  Odoo failed to create the supplier invoice/refund. Flow i_117770 ID 39 set to error state.
WARNING  No partner found with {'siren': '000000002'}
WARNING  No supplier invoice/refund found with number FAC/2026/00005
```

...alors que le partenaire existe bien avec un SIREN/TVA correct (`vat = FR18000000002`).

**Cause** : [`_match_partner_from_event()`](../../l10n_fr_einvoicing/models/fr_einvoicing_flow.py#L700-L726) construit `partner_dict = {"siren": ..., "siret": ...}`, mais `_match_partner()` (dans `base_business_document_import`) ne reconnaît que `ref`, `vat`, contact (email/tél.), `name`, `website` — les clés `siren`/`siret` sont ignorées. Le matching échoue donc systématiquement, et en cascade : la facture PDF (`i_117770`) n'est jamais créée, puis l'événement de cycle de vie (`ie_389438`) ne retrouve ni le partenaire ni la facture.

**Correctif** : le module OCA prévoit un point d'extension pour ça, `_hook_match_partner()` (retourne `False` par défaut). Surchargé dans [`models/business_document_import.py`](../models/business_document_import.py) pour chercher un `res.partner` par le champ `siren` :

```python
class BusinessDocumentImport(models.AbstractModel):
    _inherit = "business.document.import"

    def _hook_match_partner(self, partner_dict, chatter_msg, domain, order):
        siren = partner_dict.get("siren")
        if siren:
            partner = self.env["res.partner"].search(
                domain + [("siren", "=", siren)], limit=1, order=order
            )
            if partner:
                return partner
        return super()._hook_match_partner(partner_dict, chatter_msg, domain, order)
```

**Limite connue** : matche uniquement par SIREN, pas par SIRET (`invoice_issuer["0009"]`) — à étendre si besoin de distinguer plusieurs établissements d'une même entreprise.

### 3. La facture fournisseur n'est jamais créée : module `l10n_fr_einvoicing_import` manquant

Une fois le partenaire trouvé, l'import échoue encore :

```
WARNING  Odoo failed to create the supplier invoice/refund. Flow i_119024 (Téléchargé) ID 43 set to error state.
WARNING  No invoice found with domain [('ref', '=', 'FAC/2026/00005'), ('company_id', '=', 2), ...]
```

**Cause** : [`_import_supplier_invoice()`](../../l10n_fr_einvoicing/models/fr_einvoicing_flow.py#L551-L556) dans `l10n_fr_einvoicing` est **volontairement un stub qui renvoie toujours `False`** (aucune exception levée) :

```python
def _import_supplier_invoice(self, result):
    """Method inherited in l10n_fr_einvoicing_import
    If you don't want to use the OCA module account_invoice_import, you can develop
    an alternative to l10n_fr_einvoicing_import and inherit this method"""
    self.ensure_one()
    return False
```

La vraie implémentation vit dans un module séparé, non installé ici : [l10n_fr_einvoicing_import.md](./l10n_fr_einvoicing_import.md) (dépôt `akretion/fr-einvoicing`), qui dépend lui-même de [account_invoice_import.md](./account_invoice_import.md) (dépôt `OCA/edi`). Sans ces 2 modules, la facture PDF (`i_119024`) n'est jamais créée, puis l'événement de cycle de vie suivant (`ie_392435`, type `SupplierInvoiceLC`) ne trouve pas non plus de facture avec le numéro attendu (`FAC/2026/00005`) : même cascade que le problème n°2, un cran plus loin.

Vérifié que le PDF reçu de Super PDP contient bien un XML embarqué (format Factur-X, `/EmbeddedFile` + `/Filespec` dans le PDF) : `account_invoice_import` sait l'extraire nativement via `pypdf` (déjà installé sur `bookworm`), pas besoin du sous-module `account_invoice_import_invoice2data`.

**Correctif** : installer [l10n_fr_einvoicing_import.md](./l10n_fr_einvoicing_import.md) et [account_invoice_import.md](./account_invoice_import.md) (voir ces fiches pour le détail).

### 4. `KeyError: 'partner'` : module `account_invoice_import_facturx` manquant

Une fois `l10n_fr_einvoicing_import`/`account_invoice_import` installés, l'import trouve bien l'attachement Factur-X mais plante quand même :

```
INFO     Attachment 'factur-x.xml' found in PDF
INFO     Start to parse XML file factur-x.xml
WARNING  Error in creation of the supplier invoice/refund from flow i_119056 (Créé) ID 49: 'partner'
ERROR    UnboundLocalError: cannot access local variable 'err' where it is not associated with a value
```

**Cause** : `account_invoice_import` (module de base) ne sait pas lui-même parser le contenu XML — `parse_xml_invoice()` est un stub qui renvoie `False`, à surcharger par un module de format. Sans [`account_invoice_import_facturx`](./account_invoice_import_facturx.md) (+ sa dépendance [base_facturx.md](./base_facturx.md)), `parse_pdf_invoice()` retombe sur un dict `parsed_inv = {}` **vide mais pas `False`** — donc pas d'erreur explicite à ce stade — et le code suivant accède directement à `parsed_inv["partner"]` sans `.get()`, d'où le `KeyError: 'partner'` sec.

**Bug additionnel révélé au passage** (upstream `l10n_fr_einvoicing`, indépendant de ce qui précède) : cette `KeyError` est capturée par `except Exception as err:` dans [`_process()`](../../l10n_fr_einvoicing/models/fr_einvoicing_flow.py#L585-L608), mais Python supprime automatiquement la variable `err` à la sortie du bloc `except` (même si elle a été pré-initialisée à `None` avant le `try`) — le `if err:` un peu plus loin lève alors `UnboundLocalError`, ce qui fait planter tout le job d'import (au lieu de marquer juste ce flux en erreur et continuer). Ce bug ne s'était jamais déclenché avant faute d'exception réelle levée dans `_import_supplier_invoice()` (cf. problème n°3). Pas patché ici, pas encore remonté upstream.

**Correctif** : installer [account_invoice_import_facturx.md](./account_invoice_import_facturx.md) et [base_facturx.md](./base_facturx.md).

### 5. Warnings non bloquants après import : produit non trouvé + montant de taxe forcé

Une fois toute la chaîne de modules installée, l'import réussit mais poste parfois ces deux avertissements dans le chatter de la facture fournisseur créée (facture non structurée, ex. ticket de caisse Burger Queen) :

```
Odoo couldn't find any product corresponding to the following information extracted from the business document:
Barcode:
Product code:
Supplier: Burger Queen
Le montant total de taxes a été forcé à 0,00 € (le montant calculé par Odoo était de 0,36 €).
```

**Cause** : le XML Factur-X ne fournit pas d'infos produit exploitables (ni code-barres, ni code produit) ; `_match_product()` (`base_business_document_import/models/business_document_import.py:645`) échoue alors à trouver un `product.product` et retombe sur le produit générique par défaut. Pour la taxe, `account_invoice_import` recalcule la TVA à partir des lignes (ici 0,36 €), constate qu'elle ne colle pas au total déclaré dans le XML, et force le montant de taxe à 0,00 € pour faire correspondre le total TTC réellement dû (`account_invoice_import/wizard/account_invoice_import.py:1037-1093`). Ce n'est **pas bloquant** : la facture est créée quand même.

**À vérifier après import** :
1. Le montant TTC total de la facture correspond bien au montant payé.
2. Corriger manuellement le taux de TVA sur la ligne (souvent forcé à 0 par erreur).

**Pour réduire ces warnings à l'avenir** : configurer sur la fiche du fournisseur concerné (onglet Comptabilité > section *Import de facture*) un **Produit par défaut** (`invoice_import_product_id`) et/ou des **Taxes par défaut** (`invoice_import_tax_ids`), définis dans `account_invoice_import/models/res_partner.py`.

### Piège : le bouton "Importer depuis PA maintenant" n'est pas filtré par journal

Le bouton visible dans les journaux Achats **et** Ventes (`l10n_fr_einvoicing/views/account_journal.xml`) appelle en réalité `self.company_id.fr_ctc_run_import_log_action(...)` (`account_journal.py:15-18`) : la synchronisation se fait au niveau de la **société**, pas du journal cliqué. Le type de journal n'est qu'un habillage UI — `_fr_ctc_run_import` (`fr_einvoicing_flow.py:361-368`) récupère toujours les 3 mêmes types de flux, codés en dur : `SupplierInvoice`, `CustomerInvoiceLC`, `SupplierInvoiceLC`. Donc cliquer depuis le journal Achats peut tout à fait ramener des flux `CustomerInvoiceLC` (client), ce qui est trompeur si on ne s'y attend pas.

### Chaîne complète des modules requis pour l'import des factures fournisseur Super PDP

```
l10n_fr_einvoicing_import → account_invoice_import → account_invoice_import_facturx → base_facturx
                                                  └→ base_business_document_import
```
