# Module `l10n_fr_einvoicing`

**Auteur :** Akretion France  
**Version :** 18.0.1.0.1  
**Licence :** AGPL-3  
**Dépendances :** `l10n_fr_siret_account`, `pyfrctc >= 0.7` (lib Python)

---

## Objectif

Implémentation communautaire de la réforme de la **facturation électronique française (CTC)**. Le module gère l'ensemble du cycle de vie des factures électroniques échangées avec les **Plateformes de Dématérialisation Partenaires (PDP)** agréées par l'État :

- Envoi des factures de vente au format **Factur-X** ou **CII/UBL**
- Réception et import des factures fournisseur depuis la plateforme
- Suivi des **événements de cycle de vie** (statuts AFNOR : approuvée, refusée, litige, paiement…)
- Synchronisation du **répertoire national** des entreprises immatriculées à la facturation électronique
- Authentification OAuth2 (client credentials ou authorization code)

---

## Nouveaux Menus

| Menu | Parent | Description |
|------|--------|-------------|
| **France eInvoicing** | Configuration / Comptabilité | Menu racine du module |
| **Directory Line** | France eInvoicing | Liste des lignes du répertoire e-invoicing par partenaire |

Des accès rapides sont également ajoutés dans le tableau de bord des journaux de vente/achat (lien « Import from AP Now »).

---

## Nouveaux Champs

### Modèle `account.move` (Factures)

| Champ | Type | Description |
|-------|------|-------------|
| `fr_directory_line_id` | Many2one → `fr.directory.line` | Ligne de répertoire sélectionnée pour la facture |
| `fr_einvoicing_flow_id` | Many2one → `fr.einvoicing.flow` | Flux e-invoicing associé (lecture seule) |
| `fr_einvoicing_flow_state` | Selection (related) | État du flux (soumis, en attente, traité, erreur…) |
| `fr_einvoicing_flow_submitted_at` | Datetime (related) | Date d'envoi à la plateforme |
| `fr_einvoicing_event_ids` | One2many → `fr.einvoicing.event` | Événements de cycle de vie liés |
| `fr_einvoicing_last_event_id` | Many2one (calculé) | Dernier événement reçu |
| `fr_einvoicing_last_event_decoration` | Char (related) | Couleur d'affichage du dernier événement |
| `fr_einvoicing_show_readable_invoice_button` | Boolean (calculé) | Affiche le bouton « Télécharger facture lisible » |
| `fr_directory_company_entity_type` | Selection (related) | Type d'entité de la société |
| `fr_directory_partner_entity_type` | Selection (related) | Type d'entité du partenaire commercial |

### Modèle `res.partner` (Partenaires)

| Champ | Type | Description |
|-------|------|-------------|
| `fr_directory_line_ids` | One2many → `fr.directory.line` | Toutes les lignes de répertoire du partenaire |
| `fr_directory_line_active_count` | Integer (calculé) | Nombre de lignes de répertoire actives |
| `fr_directory_name` | Char (calculé) | Raison sociale dans le répertoire |
| `fr_directory_entity_type` | Selection (calculé) | Type d'entité : `private_inactive`, `private`, `public`, `no` |
| `fr_directory_closed` | Boolean (calculé) | Entité fermée dans le répertoire |
| `fr_directory_siren` | Char | SIREN utilisé pour la requête répertoire |
| `fr_directory_siret` | Char | SIRET utilisé (entités publiques) |
| `fr_directory_entity_changed_warning` | Boolean (calculé) | Alerte si SIREN/SIRET a changé depuis la dernière synchro |
| `fr_directory_last_sync_date` | Date (calculé) | Date de dernière synchronisation répertoire |
| `default_fr_directory_line_id` | Many2one → `fr.directory.line` | Ligne de répertoire par défaut |
| `fr_directory_line_show` | Boolean (calculé) | Affiche ou non le champ ligne par défaut |
| `fr_directory_show_warning_missing_siren` | Boolean (calculé) | Alerte si SIREN manquant |

### Modèle `res.company` (Sociétés)

| Champ | Type | Description |
|-------|------|-------------|
| `fr_ctc_accredited_platform` | Selection | Plateforme agréée (ex. `superpdp`) |
| `fr_ctc_auth_method` | Selection | Méthode d'authentification : `client_credentials` ou `authorization_code` |
| `fr_ctc_client_id` | Char | Client ID pour l'API |
| `fr_ctc_client_secret` | Char | Client Secret (méthode credentials) |
| `fr_ctc_last_flow_import_datetime` | Datetime | Dernière date d'import de flux |
| `fr_ctc_event_auto_send_in_hand` | Boolean | Auto-envoyer statut « In Hand » à l'import (défaut : True) |
| `fr_ctc_event_auto_send_approved` | Boolean | Auto-envoyer statut « Approved » à la confirmation (défaut : True) |
| `fr_ctc_activity_warning_event_user_ids` | Many2many → `res.users` | Utilisateurs recevant les notifications d'événements |
| `fr_ctc_activity_warning_event_invoice_creator` | Boolean | Notifier le créateur de la facture (défaut : True) |
| `fr_ctc_activity_warning_event_salesman` | Boolean | Notifier le vendeur (défaut : True) |
| `fr_ctc_directory_sync_on_invoice_post` | Selection | Synchronisation répertoire à la validation : `blocking`, `not_blocking` ou `no` |

---

## Nouveaux Modèles (tables créées)

| Modèle | Description |
|--------|-------------|
| `fr.einvoicing.flow` | Flux XML échangés avec la plateforme (entrants/sortants) |
| `fr.einvoicing.event` | Événements de cycle de vie (statuts AFNOR 200–220) |
| `fr.einvoicing.log` | Historique des synchronisations répertoire |
| `fr.einvoicing.token` | Stockage sécurisé des tokens OAuth2 par société |
| `fr.directory.line` | Lignes du répertoire national (SIREN, SIRET, code routage) |
