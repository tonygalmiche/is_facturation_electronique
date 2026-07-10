# Module `l10n_fr_pdp`

**Auteur :** Odoo SA
**Nom complet :** France - E-Invoicing (Approved Platform)
**Licence :** LGPL-3
**Dépôt :** https://github.com/odoo/odoo (`addons/l10n_fr_pdp`, branche 18.0)
**Dépendances :** `l10n_fr_account`, `account_edi_ubl_cii_tax_extension`, `account_peppol_response`, `auth_totp_mail_enforce`, `iap`

---

## Objectif

Module **officiel Odoo** (pas un module OCA/akretion) pour la facturation électronique française (réforme CTC). Il permet d'envoyer et recevoir des documents via **la plateforme agréée par Odoo lui-même** (`pdp.odoo.com`), sur le même principe que le module Peppol déjà existant dans Odoo.

C'est une alternative à l'implémentation communautaire `akretion/fr-einvoicing` (modules `l10n_fr_einvoicing` / `account_invoice_en16931`, cf. [l10n_fr_einvoicing.md](./l10n_fr_einvoicing.md) et [akretion.md](./akretion.md)) : même besoin métier (conformité à la réforme), mais **architecture radicalement différente**.

---

## Différence clé avec l'approche akretion : pas de Saxon Server

Question initiale : `l10n_fr_pdp` utilise-t-il Saxon Server pour la validation Schematron des factures, comme le fait la lib `factur-x` utilisée par `l10n_fr_einvoicing` (cf. [saxon-server.md](./saxon-server.md)) ?

**Non.** Après inspection du code source du module (dépôt `odoo/odoo`, branche 18.0) :

- Aucune trace de `saxon`, `schematron` ni de fichier `.xsl` dans tout le module `l10n_fr_pdp`.
- Le module dépend de `iap` (In-App Purchase, le framework de services cloud propriétaires d'Odoo) et de `account_peppol_response` — la même mécanique que l'intégration Peppol existante d'Odoo.
- Les seuls contrôles effectués **localement**, dans `models/account_move.py` (méthode `_get_l10n_fr_pdp_errors`), sont des règles métier simples : TVA du partenaire valide, adresse de livraison complète (rue/ville/code postal/pays), format du nom de pièce comptable. Pas de validation Schematron XSLT2 contre les schématrons officiels Factur-X/réforme.

### Architecture réelle

```
Odoo Community (client)  --IAP-->  serveurs Odoo (pdp.odoo.com)  -->  PDP / Chorus Pro / etc.
```

Le document généré par Odoo est envoyé via le framework `iap` vers l'infrastructure cloud d'Odoo (`pdp.odoo.com`), qui gère ensuite la transmission réelle vers la plateforme destinataire. **La validation Schematron (si elle existe) se fait côté serveur Odoo, pas sur l'instance auto-hébergée du client.** C'est cohérent avec les erreurs de type *"Registration denied depuis pdp.odoo.com"* remontées par des utilisateurs — le flux passe bien par les serveurs d'Odoo, pas directement du client vers la PDP.

### Comparatif

| | `l10n_fr_einvoicing` (akretion) | `l10n_fr_pdp` (Odoo SA) |
|---|---|---|
| Validation Schematron | Locale, via Saxon Server auto-hébergé | Côté serveur Odoo (opaque, hors de l'instance client) |
| Dépendance à un service cloud tiers | Non (100% auto-hébergé, hors PDP externe) | Oui (`iap`, `pdp.odoo.com`) |
| Licence | AGPL-3 | LGPL-3 |
| Composants à installer/maintenir soi-même | Saxon Server (JVM), CodeDB, lib `factur-x`/`pyfrctc` | Aucun (tout géré par Odoo côté cloud) |
| Contrôle sur l'infrastructure | Total | Dépendant d'Odoo SA |

**À retenir** : `l10n_fr_pdp` évite le besoin d'un Saxon Server local, mais introduit une dépendance à l'infrastructure cloud d'Odoo (`iap`) — pas une solution 100% auto-hébergée sans lien avec Odoo SA. Si l'objectif est de rester indépendant de tout service cloud propriétaire, l'approche akretion + Saxon Server reste pertinente malgré la complexité opérationnelle supplémentaire (JVM à faire tourner, CodeDB, pare-feu, etc., cf. [saxon-server.md](./saxon-server.md)).

---

## Composants notables du module

| Fichier | Rôle |
|---|---|
| `models/pdp_flow.py` | Construction et suivi des flux (payloads XML envoyés/reçus) |
| `models/pdp_flow_xml_builder.py` | Génération du XML du flux à partir des factures |
| `models/account_move.py` | Champs et validations métier liés au statut PDP de la facture |
| `models/account_edi_proxy_user.py` | Gestion de l'utilisateur du proxy EDI (authentification IAP) |
| `models/account_edi_xml_cii_facturx.py`, `account_edi_xml_ubl_21_fr.py` | Génération XML Factur-X (CII) et UBL adaptée France |
| `utils/cdar.py` | Utilitaires de parsing de dates au format CDAR |
| `wizard/pdp_registration.py` | Assistant d'inscription à la plateforme `pdp.odoo.com` |
| `wizard/pdp_send_wizard.py` | Assistant d'envoi manuel de documents |

---

## Sources

- Dépôt du module : https://github.com/odoo/odoo/tree/18.0/addons/l10n_fr_pdp
- Documentation officielle : https://www.odoo.com/documentation/18.0/applications/finance/fiscal_localizations/france.html#PDP
- Contexte des autres approches : [saxon-server.md](./saxon-server.md), [l10n_fr_einvoicing.md](./l10n_fr_einvoicing.md), [akretion.md](./akretion.md), [super-pdp.md](./super-pdp.md)
