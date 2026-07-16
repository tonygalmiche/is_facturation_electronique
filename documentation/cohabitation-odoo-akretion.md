# Cohabitation entre la stack Odoo native et la stack Akretion/OCA

Ce document répond à la question : **peut-on installer en même temps, dans la même base, la stack officielle Odoo (`l10n_fr_pdp`, `account_edi_ubl_cii`, `account_peppol`) et la stack communautaire Akretion/OCA (`l10n_fr_einvoicing`, `account_invoice_en16931`) ?** (cf. [l10n_fr_pdp.md](./l10n_fr_pdp.md) pour la comparaison des deux architectures et [README.md](./README.md) pour l'arbre complet des deux stacks.)

---

## Verdict

**Pas de conflit de noms de champs/modèles**, mais **risque réel de PDF Factur-X corrompu** si les deux stacks sont actives simultanément sur une même facture. Aucune des deux stacks ne déclare d'exclusion technique (`excludes` dans le manifest) l'une contre l'autre — seule l'ancienne dépendance `account_einvoice_generate` est explicitement exclue côté Akretion (cf. [account_invoice_en16931.md](./account_invoice_en16931.md)).

---

## 1. Champs : cloisonnement correct

Les deux stacks utilisent des préfixes de champs totalement distincts, sans écrasement :

| Usage | Stack Odoo native | Stack Akretion |
|---|---|---|
| Champs facture (`account.move`) | `l10n_fr_pdp_*`, `pdp_ppf_*`, `pdp_lifecycle_*` (`l10n_fr_pdp/models/account_move.py:28-116`) | `fr_ctc_*`, `fr_einvoicing_*` (cf. [l10n_fr_einvoicing.md](./l10n_fr_einvoicing.md)) |
| Format de facture électronique choisi | `invoice_edi_format` sur `res.partner` (`account_peppol/models/res_partner.py:41,67`) | `en16931_default_pdf_invoice` sur `res.company` (`account_invoice_en16931/models/res_company.py:12`) |
| Identifiant d'annuaire du partenaire | `peppol_eas` / `peppol_endpoint` | `fr_directory_siren` / `fr_directory_siret` (via `l10n_fr_siret`) |

Ces deux jeux de champs coexistent sans se marcher dessus. Effet de bord uniquement cosmétique : la fiche partenaire affiche deux sections indépendantes de "configuration e-invoicing" (une pour chaque stack), ce qui peut prêter à confusion pour l'utilisateur final si les deux modules sont installés.

---

## 2. Le vrai point de friction : génération du PDF Factur-X

Trois modules surchargent la **même méthode d'ancrage** utilisée pour insérer un XML structuré dans le PDF au moment de l'impression : `ir_actions_report._render_qweb_pdf_prepare_streams`.

| Module | Fichier | Comportement |
|---|---|---|
| `account_edi` (core) | `account_edi/models/ir_actions_report.py` | Insère les pièces jointes EDI déjà générées (`invoice.edi_document_ids` — Peppol/UBL) |
| `account_edi_ubl_cii` (core) | `account_edi_ubl_cii/models/ir_actions_report.py` | Insère en plus Factur-X pour les rapports listés dans `account.custom_templates_facturx_list` |
| `account_invoice_en16931` (Akretion) | `account_invoice_en16931/models/ir_actions_report.py` | Régénère et insère **indépendamment** son propre XML via `pypdf`, guardé seulement par `_is_invoice_report(report_ref)` et `move._get_pdf_invoice_variant()` — **sans vérifier si `edi_document_ids` contient déjà un XML inséré par le core** |

Odoo chaîne toutes les surcharges `_inherit` d'une même méthode via le MRO : quand une même facture a **à la fois** `edi_document_ids` peuplé côté Peppol/CII **et** `en16931_default_pdf_invoice` configuré côté Akretion, les trois passes s'exécutent l'une après l'autre sur le même flux PDF. Chacune manipule directement la structure bas niveau du fichier (`OdooPdfFileWriter.cloneReaderDocumentRoot` côté Odoo vs `pypdf.add_attachment` + mutation de `_root_object` côté Akretion) : risque concret de **fichiers XML embarqués en double**, ou de structure de catalogue PDF invalide — un PDF/A-3 qui ne respecte plus le format Factur-X au lieu d'un fichier propre.

---

## 3. Recommandation pratique

Les deux stacks peuvent rester installées dans la même base (aucun conflit bloquant à l'installation), mais il faut **garder un seul chemin "actif" à la fois** par société.

**Correction (vérifié en base le 2026-07-15) :** le champ `edi_format_ids` mentionné dans une première version de ce document n'existe pas dans cette base — il appartient au module `account_edi`, qui n'est **pas installé** ici (seuls `account_edi_ubl_cii`, `account_peppol`, `purchase_edi_ubl_bis3` le sont, arrivés comme dépendances `auto_install` du module Achat). Le vrai interrupteur côté core Peppol est le champ **`account_peppol_proxy_state`** sur `res.company` (`account_peppol/models/res_company.py:65`) : tant qu'il vaut `not_registered` (valeur par défaut), aucun envoi Peppol n'est possible, quelle que soit la configuration des journaux.

- **Pour utiliser la stack Akretion (recommandé ici)** : configurer `en16931_default_pdf_invoice` sur la société (déclenche l'insertion Factur-X Akretion) et **ne jamais lancer l'assistant d'enregistrement Peppol** (`account_peppol_proxy_state` doit rester `not_registered`).
- **Pour utiliser la stack officielle Odoo (`l10n_fr_pdp`)** : ne pas configurer `en16931_default_pdf_invoice` sur la société (désactive l'insertion Akretion), et faire l'enregistrement Peppol via l'assistant dédié.

Ne jamais activer les deux configurations en même temps sur la même société — ce cas n'est pas testé/protégé par le code et produit un PDF potentiellement corrompu à l'impression d'une facture.

### État vérifié sur `facturation-electronique18` (2026-07-15)

| Société | `en16931_default_pdf_invoice` (Akretion) | `account_peppol_proxy_state` (core) | `fr_ctc_accredited_platform` | `fr_ctc_send_invoice_format` |
|---|---|---|---|---|
| InfoSaône | `facturx` | `not_registered` | `superpdp` | `facturx` |
| Burger Queen | `facturx` | `not_registered` | `superpdp` | `facturx` |
| Tricatel | `facturx` | `not_registered` | `superpdp` | `facturx` |

→ **Configuration saine** : la stack Akretion (Super PDP + Factur-X) est bien active sur les 3 sociétés, et la stack core Peppol est bien inactive (`not_registered`) sur les 3 — donc pas de risque de double insertion PDF dans l'état actuel. Point de vigilance : ne pas lancer l'assistant d'enregistrement Peppol côté Comptabilité par erreur, ce qui basculerait `account_peppol_proxy_state` hors de `not_registered` et réactiverait le risque décrit en section 2.

---

## Origine de cette analyse

Investigation menée suite à l'installation du module Achat (`purchase`), qui a entraîné l'installation de `purchase_edi_ubl_bis3` → `account_edi_ubl_cii` (cf. incident documenté dans [account_edi_ubl_cii.md](./account_edi_ubl_cii.md)). Cette installation a fait cohabiter pour la première fois dans cette base les deux stacks EDI, d'où la vérification de compatibilité ci-dessus.
