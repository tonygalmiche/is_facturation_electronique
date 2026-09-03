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

---

## Retour d'expérience : import d'une facture Bouygues Telecom (Super PDP)

| Problème | Erreur observée | Cause | Solution |
|---|---|---|---|
| Facture jamais créée | Flux en `Erreur` : `Error: 'partner'` | `account_invoice_import_facturx` et `base_facturx` non installés → le XML Factur-X embarqué dans le PDF n'était jamais parsé, `parsed_inv` restait vide | Installer `base_facturx` + `account_invoice_import_facturx` |
| Compte comptable invalide | `Le compte 506500 est de type débiteur, mais est utilisé dans une opération d'achat` | `default_account_id` du journal achat (FACTU) mal configuré (compte de classe 5 au lieu d'un compte de charge classe 6) — utilisé par défaut faute de produit matché sur les lignes | Corriger le compte par défaut du journal "Factures fournisseurs" |
| Fournisseur non retrouvé | Avertissement "Odoo couldn't find any partner" | Aucun `res.partner` avec ce n° de TVA en base | Créer le partenaire via le bouton "Créer ou mettre à jour un partenaire" — le matching se fait ensuite automatiquement par n° de TVA/SIRET |
| Ré-import bloqué (doublon) | Échec silencieux, sans détail d'erreur | `_invoice_already_exists` retrouve la facture déjà créée (même réf + partenaire + société), même si elle est annulée | Pas de solution "propre" : la facture liée à un flux ne peut être ni supprimée ni écartée du contrôle de doublon (`account_move.unlink()` bloqué). Pour retester, changer la `Référence` de l'ancienne facture |
| Produits non retrouvés | Avertissement "Odoo couldn't find any product" (comptes de lignes tous identiques) | Le XML Bouygues ne fournit ni code-barres ni code produit (`SellerAssignedID`) par ligne — le matching standard (`_match_product`) ne peut rien faire | Surcharge ajoutée dans `is_gestion_odoo18` (`models/business_document_import.py` + `wizards/account_invoice_import.py`) : matching par désignation (nom de ligne) en dernier recours |

**Points clés à retenir :**
- Vérifier systématiquement que les 5 modules du "Cas 3" (voir commentaires dans `is_facturation_electronique/__manifest__.py`) sont bien installés, pas seulement déclarés en dépendance.
- Une facture liée à un `fr.einvoicing.flow` est indélébile (par design, traçabilité) — bien vérifier les données de test avant de lancer un import réel.
- Le matching produit OCA ne se fait que par identifiant (code-barres/référence/code fournisseur), jamais par désignation nativement.
