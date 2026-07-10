## Présentation de la librairie `pyfrctc`

**Source :** https://github.com/akretion/pyfrctc
**Auteur :** Alexis de Lattre (Akretion)
**Licence :** LGPL-2.1+
**Version actuelle :** 0.7 (2026-05-28)
**Statut :** Beta (noms de méthodes et arguments peuvent encore changer)

### Objectif

`pyfrctc` est une librairie Python fournissant des méthodes utilitaires pour la **facturation électronique** et le **e-Reporting** en France. Elle implémente le standard **AFNOR XP Z12-013** qui définit les APIs des Plateformes Agréées (PA). Elle est utilisée en priorité par le module communautaire Odoo `l10n_fr_einvoicing`, mais peut être réutilisée par n'importe quel logiciel.

### Dépendances

- `requests_oauthlib` — gestion OAuth2
- `python-stdnum >= 1.20` — validation SIREN/SIRET
- `lxml` — parsing/génération XML
- `saxonche` — transformation XSLT (validation Schematron CDAR)
- `pytz` — gestion des fuseaux horaires

### Plateformes supportées

- **SUPER PDP** (`superpdp`) — testée et validée
- Architecture extensible : d'autres plateformes conformes AFNOR peuvent être ajoutées

### Authentification OAuth2 (2 modes)

| Mode | Méthodes |
|------|----------|
| `client_credentials` (B2B machine-to-machine) | `get_session()` |
| `authorization_code` (OAuth PKCE, flux utilisateur) | `get_authorization_url()`, `authorization_code_first_token()`, `get_session()` |

### API Annuaire (`afnor-directory`)

| Méthode | Description |
|---------|-------------|
| `healthcheck(session, type="directory")` | Vérifie la disponibilité de l'API |
| `get_directory_siren(session, siren)` | Recherche un SIREN dans l'annuaire |
| `get_directory_siren_parsed(session, siren)` | Idem, retourne un dict simplifié (`name`, `closed`, `entity_type`) |
| `get_directory_siret(session, siret)` | Recherche un SIRET dans l'annuaire |
| `get_directory_siret_parsed(session, siret)` | Idem, retourne adresse + données B2G (service/engagement) |
| `get_directory_lines(session, siren_or_siret)` | Liste les lignes d'annuaire (identifiants d'adressage) avec pagination automatique |
| `get_directory_lines_parsed(...)` | Idem, version simplifiée avec filtrage optionnel des lignes Factures Publiques |

### API Flux (`afnor-flow`)

| Méthode | Description |
|---------|-------------|
| `send_flow(session, file_bin, filename, flow_syntax, processing_rule)` | Envoie une facture (syntaxes : `CII`, `UBL`, `Factur-X`, `CDAR`, `FRR`) |
| `send_flow_parsed(...)` | Idem avec retour parsé |
| `search_flows(session, updated_after, flow_direction, flow_type, ...)` | Recherche des flux avec pagination automatique (filtre par direction, type, date) |
| `search_flows_parsed(...)` | Idem avec normalisation des clés retournées |
| `get_flow(session, flow_id, doc_type=None)` | Récupère un flux par son ID (métadonnées ou document) |
| `get_flow_metadata_parsed(session, flow_id)` | Récupère les métadonnées d'un flux, version parsée |

### Gestion du cycle de vie — CDAR XML

Les fichiers CDAR (*Cross Domain Acknowledgement and Response*) permettent de gérer le cycle de vie des factures électroniques.

| Méthode | Description |
|---------|-------------|
| `generate_cdar(data_dict, check_xsd=True, check_schematron=True)` | Génère un fichier XML CDAR validé par XSD et Schematron |

Fichiers de validation embarqués :
- XSD : `CrossDomainAcknowledgementAndResponse_100pD22B.xsd`
- Schematron XSL : `20260430_BR-FR-CDV-Schematron-CDAR_V1.3.1.xsl`

### Types de flux supportés

- `CustomerInvoice` / `SupplierInvoice` / `StateInvoice`
- Variantes cycle de vie (`LC`) : `CustomerInvoiceLC`, `SupplierInvoiceLC`, `StateCustomerInvoiceLC`, `StateSupplierInvoiceLC`
- Règles de traitement : `B2B`, `B2BInt`, `B2C`, `B2G`, `B2GInt`, `OutOfScope`, `B2GOutOfScope`, `ArchiveOnly`, `NotApplicable`



### Installation

Depuis Debian Bookworm, `pip install` est bloqué par défaut (PEP 668). Les options ci-dessous s'appliquent selon le contexte.


**Installation dans le home utilisateur (`--user`) sans droits root**

Sur Debian Bookworm, ajouter `--break-system-packages` (installe dans `~/.local/`, pas dans le système) :

```bash
pip install --user --break-system-packages git+https://github.com/akretion/pyfrctc.git
```

Le risque est limité : ça n'écrase rien dans les packages système Debian.


**Depuis PyPI (quand disponible) :**
```bash
pip install --user --break-system-packages pyfrctc
```


> Les dépendances `lxml`, `pytz` et `python-stdnum` sont disponibles via apt (`python3-lxml`, `python3-tz`, `python3-stdnum`). `saxonche` et `requests-oauthlib` nécessitent pip.


