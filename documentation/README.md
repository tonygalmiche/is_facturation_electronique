# Index — Arbre des dépendances des modules

Ce projet couvre **deux architectures distinctes** pour la facturation électronique française (cf. [l10n_fr_pdp.md](./l10n_fr_pdp.md) pour la comparaison) :

1. **Stack communautaire Akretion/OCA** — auto-hébergée, nécessite [Saxon Server](./saxon-server.md)
2. **Module officiel Odoo `l10n_fr_pdp`** — s'appuie sur l'infrastructure cloud d'Odoo SA

Les modules sans lien (texte simple) sont des modules natifs d'Odoo non documentés séparément dans ce dossier (pas de spécificité liée à la réforme).

## Installation rapide

Le script [`installation-modules-oca.sh`](./installation-modules-oca.sh) automatise le téléchargement et la mise en place des modules OCA/Akretion de la stack communautaire, selon le cas d'installation souhaité (cf. [installation.md](./installation.md)) :

```bash
./installation-modules-oca.sh <cas:1|2|3> [dossier_destination]
# par défaut : /media/sf_dev_odoo/18.0/facturation-electronique
#   1 : génération Factur-X/EN16931, sans envoi sur la PA (section 1 ci-dessous)
#   2 : cas 1 + envoi de la facture sur la PA
#   3 : cas 2 + réception des factures fournisseurs depuis la PA (section 2 ci-dessous)
```

Ne gère pas les libs Python (`factur-x`, `pyfrctc`) ni Saxon Server — voir [lib-factur-x.md](./lib-factur-x.md), [lib-pyfrctc.md](./lib-pyfrctc.md), [saxon-server.md](./saxon-server.md).

---

## 1. Stack communautaire Akretion/OCA

```
l10n_fr_einvoicing                                   (Akretion, cf. l10n_fr_einvoicing.md)
├── l10n_fr_siret_account                            (OCA/l10n-france, cf. l10n_fr_siret_account.md)
│   ├── l10n_fr_siret                                (OCA/l10n-france, cf. l10n_fr_siret.md)
│   │   ├── l10n_fr                                  [natif Odoo]
│   │   └── base_view_inheritance_extension          (OCA/server-tools, cf. base_view_inheritance_extension.md)
│   └── l10n_fr_account                              (natif Odoo, cf. l10n_fr_account.md)
│       ├── base_iban                                [natif Odoo]
│       ├── base_vat                                 (natif Odoo, cf. base_vat.md)
│       ├── account                                  [natif Odoo]
│       └── l10n_fr                                  [natif Odoo]
├── l10n_fr_account_invoice_en16931                  (Akretion, cf. l10n_fr_account_invoice_en16931.md)
│   ├── account_invoice_en16931                      (Akretion, cf. account_invoice_en16931.md)
│   │   ├── account_tax_unece                        (OCA/community-data-files + PR VATEX, cf. account_tax_unece.md)
│   │   │   └── base_unece                           (OCA/community-data-files, cf. base_unece.md)
│   │   ├── uom_unece                                (OCA/community-data-files, cf. uom_unece.md)
│   │   ├── account_payment_unece                    (OCA/community-data-files, cf. account_payment_unece.md)
│   │   │   ├── base_unece                           (cf. base_unece.md)
│   │   │   └── account_payment_method_base          (OCA/account-payment, cf. account_payment_method_base.md)
│   │   ├── base_vat                                 (cf. base_vat.md)
│   │   └── intrastat_base                           (OCA/intrastat-extrastat, cf. intrastat_base.md)
│   │       └── base_vat                             (cf. base_vat.md)
│   └── l10n_fr_siret                                (cf. l10n_fr_siret.md)
├── lib Python `pyfrctc` >= 0.7                      (cf. lib-pyfrctc.md)
└── lib Python `factur-x` >= 6.1                     dépendance de account_invoice_en16931 (cf. lib-factur-x.md)

Composant externe obligatoire (pas un module Odoo) :
Saxon Server (cf. saxon-server.md) — appelé en HTTP par les libs pyfrctc ET factur-x
```

**Autres dépendances mentionnées dans les modules ci-dessus, non documentées ici** (natives Odoo ou hors périmètre) : `account`, `uom`, `l10n_fr`.

---

## 2. Import des factures fournisseur (Super PDP)

Complète la stack 1 : sans ces modules, `l10n_fr_einvoicing` ne fait que **recevoir** les flux mais ne crée jamais la facture fournisseur correspondante (cf. [import-depuis-super-pdp.md](./import-depuis-super-pdp.md) pour le détail des incidents rencontrés). Installation : `./installation-modules-oca.sh 3` (cf. ci-dessus).

```
l10n_fr_einvoicing_import                            (Akretion, cf. l10n_fr_einvoicing_import.md)
├── l10n_fr_einvoicing                               (cf. arbre 1 ci-dessus)
└── account_invoice_import                           (OCA/edi, cf. account_invoice_import.md)
    ├── base_business_document_import                (OCA/edi, cf. base_business_document_import.md)
    │   ├── account_tax_unece                        (cf. arbre 1 ci-dessus)
    │   └── uom_unece                                (cf. arbre 1 ci-dessus)
    ├── base_iban                                    [natif Odoo]
    └── account                                      [natif Odoo]

Pour parser le XML CII/Factur-X embarqué dans le PDF fournisseur (sinon parse_xml_invoice()
reste un stub qui échoue silencieusement, cf. import-depuis-super-pdp.md #4) :
account_invoice_import_facturx                       (OCA/edi, cf. account_invoice_import_facturx.md)
├── account_invoice_import                           (ci-dessus)
└── base_facturx                                     (OCA/edi, cf. base_facturx.md)
    ├── uom_unece                                    (cf. arbre 1 ci-dessus)
    ├── account_tax_unece                            (cf. arbre 1 ci-dessus)
    └── account_payment_unece                        (cf. arbre 1 ci-dessus)
```

---

## 3. Module officiel Odoo `l10n_fr_pdp`

```
l10n_fr_pdp (Odoo SA, cf. l10n_fr_pdp.md)
├── l10n_fr_account (cf. l10n_fr_account.md)
├── account_edi_ubl_cii_tax_extension                [natif Odoo]
├── account_peppol_response                          [natif Odoo]
├── auth_totp_mail_enforce                           [natif Odoo]
└── iap (In-App Purchase, service cloud Odoo)        [natif Odoo]
```

---

## Tableau des modules (même ordre que l'arbre)

| Module | Origine | Description courte |
|---|---|---|
| [`l10n_fr_einvoicing`](./l10n_fr_einvoicing.md) | Akretion | Cycle de vie complet des factures électroniques françaises (envoi, réception, annuaire, événements) |
| [`l10n_fr_siret_account`](./l10n_fr_siret_account.md) | OCA/l10n-france | Auto-install reliant SIRET (partenaires) et comptabilité française |
| [`l10n_fr_siret`](./l10n_fr_siret.md) | OCA/l10n-france | Champs SIREN/NIC/SIRET validés (checksum, décomposition, doublons) |
| [`base_view_inheritance_extension`](./base_view_inheritance_extension.md) | OCA/server-tools | Dépendance technique cachée pour l'héritage de vues |
| [`l10n_fr_account`](./l10n_fr_account.md) | natif Odoo | Localisation comptable française (plan comptable, taxes, export FEC) |
| [`base_vat`](./base_vat.md) | natif Odoo | Validation du format des numéros de TVA intracommunautaire |
| [`l10n_fr_account_invoice_en16931`](./l10n_fr_account_invoice_en16931.md) | Akretion | Surcouche France de la génération EN16931 (SIREN/SIRET, mentions légales de paiement) |
| [`account_invoice_en16931`](./account_invoice_en16931.md) | Akretion | Génération générique Factur-X/UBL conforme EN16931, config Saxon Server |
| [`account_tax_unece`](./account_tax_unece.md) | OCA/community-data-files (+ PR VATEX) | Codes UNECE type/catégorie de taxe + motifs d'exonération VATEX |
| [`base_unece`](./base_unece.md) | OCA/community-data-files | Modèle générique `unece.code.list` pour toutes les nomenclatures UNECE |
| [`uom_unece`](./uom_unece.md) | OCA/community-data-files | Code UNECE sur les unités de mesure (`uom.uom`) |
| [`account_payment_unece`](./account_payment_unece.md) | OCA/community-data-files | Code UNECE sur les moyens de paiement |
| [`account_payment_method_base`](./account_payment_method_base.md) | OCA/account-payment | Vues manquantes pour `account.payment.method` |
| [`intrastat_base`](./intrastat_base.md) | OCA/intrastat-extrastat | Socle technique des déclarations Intrastat (biens/services, régime fiscal) |
| [lib Python `pyfrctc`](./lib-pyfrctc.md) | Akretion (PyPI) | API AFNOR XP Z12-013 (annuaire, flux, CDAR) — appelle Saxon Server |
| [lib Python `factur-x`](./lib-factur-x.md) | Akretion (PyPI) | Génération XML Factur-X/UBL — appelle Saxon Server pour la validation Schematron |
| [Saxon Server](./saxon-server.md) | willemvlh (externe) | Serveur HTTP de validation Schematron (XSLT2), composant obligatoire non-Odoo |
| [`l10n_fr_einvoicing_import`](./l10n_fr_einvoicing_import.md) | Akretion | Implémente réellement l'import des factures fournisseur reçues de Super PDP |
| [`account_invoice_import`](./account_invoice_import.md) | OCA/edi | Import générique de factures fournisseur PDF/XML, matching via `business.document.import` |
| [`base_business_document_import`](./base_business_document_import.md) | OCA/edi | Modèle abstrait `business.document.import` : méthodes de matching (partenaire, produit, taxe...) |
| [`account_invoice_import_facturx`](./account_invoice_import_facturx.md) | OCA/edi | Parsing du XML CII/Factur-X embarqué dans un PDF fournisseur |
| [`base_facturx`](./base_facturx.md) | OCA/edi | Socle technique (mapping UNECE) requis par `account_invoice_import_facturx` |
| [`l10n_fr_pdp`](./l10n_fr_pdp.md) | Odoo SA | Facturation électronique via la plateforme cloud `pdp.odoo.com` |

## Documents transverses

- [akretion.md](./akretion.md) — annonce et contexte de la réécriture Factur-X/UBL par Alexis de Lattre (versions des libs, choix d'architecture)
- [backport-16.0.md](./backport-16.0.md) — annonce de la disponibilité des modules pour Odoo 16 et vérification des dépôts/dépendances pour ce module
- [super-pdp.md](./super-pdp.md) — plateforme PDP utilisée pour les tests
