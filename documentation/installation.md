# Installation : modules selon les besoins du client

Liste des modules à installer selon le niveau d'intégration avec une
Plateforme Agréée (PA/PDP) souhaité par le client :

1. génération d'une facture électronique Factur-X/EN16931 valide et
   vérifiée, sans transmission via une PA ;
2. génération et envoi de la facture sur la PA ;
3. génération, envoi de la facture sur la PA, et réception des factures
   fournisseurs depuis la PA.

Chaque cas ajoute des modules à celui qui le précède.

## Cas : générer une facture, sans l'envoyer sur la PA

| Module | Rôle |
|---|---|
| [account_invoice_en16931.md](account_invoice_en16931.md) | Génère et valide le Factur-X/UBL EN16931 |
| [l10n_fr_account_invoice_en16931.md](l10n_fr_account_invoice_en16931.md) | Surcouche France (mentions légales FR) |
| [l10n_fr_siret.md](l10n_fr_siret.md) | SIREN/NIC/SIRET sur les partenaires |
| [account_tax_unece.md](account_tax_unece.md) | Codes UNECE des taxes + motifs VATEX |
| [uom_unece.md](uom_unece.md) | Codes UNECE des unités de mesure |
| [account_payment_unece.md](account_payment_unece.md) | Codes UNECE des moyens de paiement |
| [base_unece.md](base_unece.md) | Modèle générique des nomenclatures UNECE |
| [intrastat_base.md](intrastat_base.md) | Socle des déclarations Intrastat |
| [base_view_inheritance_extension.md](base_view_inheritance_extension.md) | Dépendance technique (héritage de vues), requis par `l10n_fr_siret` |
| [account_payment_method_base.md](account_payment_method_base.md) | Vues `account.payment.method`, requis par `account_payment_unece` |
| [base_vat.md](base_vat.md) | Déjà dans Odoo core |

### Dépendances techniques hors modules Odoo

- Lib Python `factur-x>=6.3` — [lib-factur-x.md](lib-factur-x.md)
- Saxon Server pour la validation Schematron EN16931 — [saxon-server.md](saxon-server.md)

### Validation Saxon obligatoire

Par défaut, un échec de communication avec Saxon Server est ignoré
silencieusement par la lib `factur-x` (comportement non modifiable côté
Odoo). Le module `is_facturation_electronique` ajoute l'option
*Obliger la validation Schematron Saxon* (réglage
`is_facturation_electronique.force_saxon_validation`) qui refait le contrôle
Schematron en bloquant la facture (`UserError`) si Saxon Server est
injoignable ou si le fichier ne passe pas la validation — cf.
`models/account_move.py` et `models/res_config_settings.py`.

## Cas : générer une facture et l’envoyer sur la PA

Modules à ajouter en plus de la partie précédente :

| Module | Rôle |
|---|---|
| [l10n_fr_einvoicing.md](l10n_fr_einvoicing.md) | Flux CTC réel : envoi/réception via PPF/PDP |
| [l10n_fr_siret_account.md](l10n_fr_siret_account.md) | Lien SIRET / écritures comptables |

### Dépendances techniques hors modules Odoo

- Lib Python `pyfrctc>=0.12` — [lib-pyfrctc.md](lib-pyfrctc.md)

## Cas : générer une facture, l'envoyer sur la PA et recevoir les factures fournisseurs de la PA

Modules à ajouter en plus des deux parties précédentes :

| Module | Rôle |
|---|---|
| [l10n_fr_einvoicing_import.md](l10n_fr_einvoicing_import.md) | Import réel des factures fournisseur reçues via PA |
| [account_invoice_import.md](account_invoice_import.md) | Import générique de factures fournisseur PDF/XML |
| [account_invoice_import_facturx.md](account_invoice_import_facturx.md) | Parsing du XML CII/Factur-X d'une facture fournisseur |
| [base_facturx.md](base_facturx.md) | Socle technique requis par `account_invoice_import_facturx` |
| [base_business_document_import.md](base_business_document_import.md) | Modèle `business.document.import`, requis par les modules d'import |

## Script d'installation

[installation-modules-oca.sh](installation-modules-oca.sh)
