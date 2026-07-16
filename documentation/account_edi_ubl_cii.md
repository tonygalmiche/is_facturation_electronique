# Module `account_edi_ubl_cii`

**Auteur :** Odoo SA
**Version :** 1.0 (`account_edi_ubl_cii/__manifest__.py`, pas de suivi de version fine — le numéro ne bouge pas à chaque commit)
**Licence :** LGPL-3
**Origine :** module natif Odoo (`/opt/odoo18/addons`), `auto_install: True`, dépend de `account`
**Dépendances (côté factures fournisseur EDI) :** aucune dans ce dépôt — module standard livré avec Odoo

---

## Objectif

Module natif Odoo (pas OCA/Akretion) qui fournit l'infrastructure d'**export et d'import de factures électroniques structurées** aux formats UBL et CII : E-FFF, UBL Bis 3 (PEPPOL), EHF3, NLCIUS, Factur-X (CII), XRechnung (UBL). C'est le socle sur lequel s'appuient à la fois le module officiel `l10n_fr_pdp` (cf. arbre 3 du [README](./README.md)) et les modules d'achat EDI (`purchase_edi_ubl_bis3`, `account_peppol`).

Contrairement au reste de la stack Akretion/OCA documentée dans ce dossier (qui réimplémente sa propre génération EN16931 via Saxon Server, cf. [account_invoice_en16931.md](./account_invoice_en16931.md)), ce module encode les mêmes formats directement en XSLT/QWeb Odoo, sans dépendance externe.

Le format effectivement utilisé pour une facture est choisi sur le journal (*Journal > Réglages avancés*).

---

## Hiérarchie des modèles (AbstractModel, `_name` + `_inherit` en chaîne)

```
account.edi.common
└── account.edi.ubl                    (_name = "account.edi.ubl")
    ├── account.edi.ubl_cen_en16931
    ├── account.edi.ubl_pint
    │   └── account.edi.ubl_pint_eu    (hérite ubl_pint + ubl_cen_en16931)
    ├── account.edi.xml.ubl_20
    │   └── account.edi.xml.ubl_21
    │       └── account.edi.xml.ubl_bis3   (hérite ubl_21 + ubl_pint_eu)
    ├── account.edi.xml.ubl_a_nz
    ├── account.edi.xml.ubl_efff
    ├── account.edi.xml.ubl_nlcius
    ├── account.edi.xml.ubl_sg
    └── account.edi.xml.ubl_xrechnung
```

Chacun de ces modèles est un `AbstractModel` avec son propre `_name` : Odoo crée une ligne `ir.model` (et les lignes `ir.model.inherit` correspondantes) pour chacun d'entre eux lors de l'installation/mise à jour du module. C'est ce mécanisme de réflexion qui a été à l'origine de l'incident décrit ci-dessous.

---

## Incident : `NOT NULL` sur `ir_model_inherit.parent_id` à l'installation de `purchase_edi_ubl_bis3`

### Symptôme

```
Loading module purchase_edi_ubl_bis3 (63/74)
ERROR: bad query: INSERT INTO "ir_model_inherit" (...) VALUES (561, 496, NULL), (561, NULL, NULL), ...
ERROR: une valeur NULL viole la contrainte NOT NULL de la colonne « parent_id » dans la relation « ir_model_inherit »
```

L'installation du module Achat plante alors qu'elle ne fait qu'installer sa dépendance `purchase_edi_ubl_bis3`, dont le modèle `purchase.edi.xml.ubl_bis3` hérite de `account.edi.xml.ubl_bis3` (ce module-ci).

### Cause

Diagnostiqué en interrogeant en direct le registry Odoo (`odoo-bin shell`) : `account.edi.xml.ubl_bis3` hérite (`_inherit`) de `account.edi.xml.ubl_21` **et** `account.edi.ubl_pint_eu`. Ce dernier (support PEPPOL/PINT) est une addition récente du code sur disque — mais dans la base concernée, le module `account_edi_ubl_cii` était toujours à l'état `installed` sans jamais avoir été remis à jour (`-u`) depuis ce changement.

Résultat : `account.edi.ubl_pint_eu` (et ses propres parents `account.edi.ubl_pint`, `account.edi.ubl_cen_en16931`, `account.edi.ubl`) n'existaient tout simplement pas dans `ir_model` de cette base, alors qu'ils sont bien définis dans le code source (`_name = "account.edi.ubl_pint_eu"`, etc.). Le mécanisme `ModelInherit._reflect_inherits()` (`odoo/addons/base/models/ir_model.py`) fait `get_model_id(parent_name)` pour chaque parent déclaré ; pour un modèle absent de `ir_model`, cette fonction renvoie `None` → tentative d'insertion d'une ligne `ir_model_inherit` avec `parent_id = NULL` → violation de la contrainte `NOT NULL` (le champ est `required=True`).

En résumé : **le code du module a évolué (ajout du support PINT/PEPPOL) sans que le module ne soit remis à jour dans cette base**, ce qui a laissé des métadonnées `ir.model` incomplètes.

### Correctif

Mettre à jour `account_edi_ubl_cii` (et par prudence `account_peppol`, qui étend lui aussi `account.edi.xml.ubl_bis3`) **avant** d'installer `purchase`/`purchase_edi_ubl_bis3`, pour que les nouveaux modèles intermédiaires soient correctement réfléchis dans `ir_model`/`ir_model_inherit` :

```bash
/opt/odoo18/odoo-bin -c /etc/odoo/facturation-electronique18.conf -d facturation-electronique18 \
  -u account_edi_ubl_cii,account_peppol --stop-after-init
```

Puis relancer l'installation du module Achat normalement depuis l'interface.

**À retenir** : après toute mise à jour du code source d'Odoo (`git pull`, changement de commit sur `/opt/odoo18`), penser à faire un `-u base` (ou au minimum `-u` sur les modules natifs dont le code a changé) avant d'installer de nouveaux modules qui en dépendent — un simple redémarrage du serveur ne suffit pas à réconcilier les métadonnées `ir.model` avec le code sur disque tant que le module reste à l'état `installed`.
