# Lib Python `pyfrctc`

**Paquet PyPI :** `pyfrctc`
**Auteur :** Alexis de Lattre (Akretion)
**Licence :** LGPL-2.1+
**Version utilisée par la réforme (cf. [akretion.md](./akretion.md)) :** 0.13
**Dépôt :** https://github.com/akretion/pyfrctc
**Statut :** Beta (noms de méthodes et arguments peuvent encore changer)
**Rôle :** implémente le standard **AFNOR XP Z12-013** (API des Plateformes Agréées / PDP) : authentification OAuth2, requêtes d'annuaire (SIREN/SIRET), envoi/recherche de flux, génération des fichiers CDAR de cycle de vie. Utilisée en priorité par le module communautaire Odoo `l10n_fr_einvoicing`, mais réutilisable par n'importe quel logiciel.

Dépendances (installées automatiquement par pip) : `lxml`, `python-dateutil`, `python-stdnum>=1.20`, `pytz`, `requests`, `requests-oauthlib`. Nécessite Python ≥ 3.9.

Comme `factur-x`, `pyfrctc` 0.13 ne dépend plus de `saxonche` : la validation Schematron des fichiers **CDAR** (fonction `check_cdar_schematron`) passe par une requête HTTP vers [Saxon Server](./saxon-server.md) (même changement, motivé par le même bug GraalVM : https://github.com/akretion/pyfrctc/issues/3). Rien à installer côté `saxonche` pour cette lib. (Dans les versions antérieures à la 0.13, `saxonche` était encore une dépendance directe — obsolète depuis ce changement.)

## Plateformes supportées

- **SUPER PDP** (`superpdp`) — testée et validée
- Architecture extensible : d'autres plateformes conformes AFNOR peuvent être ajoutées

## Authentification OAuth2 (2 modes)

| Mode | Méthodes |
|------|----------|
| `client_credentials` (B2B machine-to-machine) | `get_session()` |
| `authorization_code` (OAuth PKCE, flux utilisateur) | `get_authorization_url()`, `authorization_code_first_token()`, `get_session()` |

## API Annuaire (`afnor-directory`)

| Méthode | Description |
|---------|-------------|
| `healthcheck(session, type="directory")` | Vérifie la disponibilité de l'API |
| `get_directory_siren(session, siren)` | Recherche un SIREN dans l'annuaire |
| `get_directory_siren_parsed(session, siren)` | Idem, retourne un dict simplifié (`name`, `closed`, `entity_type`) |
| `get_directory_siret(session, siret)` | Recherche un SIRET dans l'annuaire |
| `get_directory_siret_parsed(session, siret)` | Idem, retourne adresse + données B2G (service/engagement) |
| `get_directory_lines(session, siren_or_siret)` | Liste les lignes d'annuaire (identifiants d'adressage) avec pagination automatique |
| `get_directory_lines_parsed(...)` | Idem, version simplifiée avec filtrage optionnel des lignes Factures Publiques |

## API Flux (`afnor-flow`)

| Méthode | Description |
|---------|-------------|
| `send_flow(session, file_bin, filename, flow_syntax, processing_rule)` | Envoie une facture (syntaxes : `CII`, `UBL`, `Factur-X`, `CDAR`, `FRR`) |
| `send_flow_parsed(...)` | Idem avec retour parsé |
| `search_flows(session, updated_after, flow_direction, flow_type, ...)` | Recherche des flux avec pagination automatique (filtre par direction, type, date) |
| `search_flows_parsed(...)` | Idem avec normalisation des clés retournées |
| `get_flow(session, flow_id, doc_type=None)` | Récupère un flux par son ID (métadonnées ou document) |
| `get_flow_metadata_parsed(session, flow_id)` | Récupère les métadonnées d'un flux, version parsée |

## Gestion du cycle de vie — CDAR XML

Les fichiers CDAR (*Cross Domain Acknowledgement and Response*) permettent de gérer le cycle de vie des factures électroniques.

| Méthode | Description |
|---------|-------------|
| `generate_cdar(data_dict, check_xsd=True, check_schematron=True)` | Génère un fichier XML CDAR validé par XSD et Schematron (via [Saxon Server](./saxon-server.md), cf. plus haut) |

Fichiers de validation embarqués :
- XSD : `CrossDomainAcknowledgementAndResponse_100pD22B.xsd`
- Schematron XSL : `20260430_BR-FR-CDV-Schematron-CDAR_V1.3.1.xsl`

## Types de flux supportés

- `CustomerInvoice` / `SupplierInvoice` / `StateInvoice`
- Variantes cycle de vie (`LC`) : `CustomerInvoiceLC`, `SupplierInvoiceLC`, `StateCustomerInvoiceLC`, `StateSupplierInvoiceLC`
- Règles de traitement : `B2B`, `B2BInt`, `B2C`, `B2G`, `B2GInt`, `OutOfScope`, `B2GOutOfScope`, `ArchiveOnly`, `NotApplicable`

## Installation

Disponible sur PyPI depuis la version 0.13 (avant ça, install directe depuis GitHub). Même convention que pour [factur-x](./lib-factur-x.md) sur nos VPS Odoo : pas de venv, install system-wide en root.

```bash
apt install python3-oauthlib python3-requests-oauthlib
apt install python3-pip
apt install python3-packaging
apt install unicode

su odoo
pip install unidecode
pip install pyfrctc
pip show pyfrctc
Version: 0.15
```



## Vérifier ce qui est installé

```bash
pip3 show pyfrctc
```

## Piège : Odoo peut voir une autre version que celle installée en root

Même piège que pour [factur-x](./lib-factur-x.md#piège--odoo-peut-voir-une-autre-version-que-celle-installée-en-root) : Odoo tourne sous l'utilisateur `odoo`, pas `root`. Si un `pip install --user` a été fait par le passé sous ce compte, `~/.local/lib/python3.X/site-packages/` (prioritaire dans `sys.path`) masque la version system-wide installée en root.

Constaté en pratique sur `bookworm` :

```bash
# root voit la bonne version :
pip3 show pyfrctc | grep -E "Version|Location"
# Version: 0.13
# Location: /usr/local/lib/python3.11/dist-packages

# odoo voit une vieille version dev :
su - odoo -c "pip3 show pyfrctc" | grep -E "Version|Location"
# Version: 0.8.dev2+gef287c7f0
# Location: /home/odoo/.local/lib/python3.11/site-packages
```

Correction — désinstaller **en tant qu'utilisateur `odoo`**, pas en root, pour cibler le bon `site-packages` :

```bash
su - odoo -c "pip3 uninstall --break-system-packages -y pyfrctc"
```

## Sources

- [akretion.md](./akretion.md) — contexte de la réforme et versions utilisées
- [lib-factur-x.md](./lib-factur-x.md) — lib complémentaire (génération Factur-X/UBL)
- [saxon-server.md](./saxon-server.md) — service externe requis pour la validation Schematron (Factur-X **et** CDAR)
