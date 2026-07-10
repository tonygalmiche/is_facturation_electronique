# Lib Python `pyfrctc`

**Paquet PyPI :** `pyfrctc`
**Version utilisée par la réforme (cf. [akretion.md](./akretion.md)) :** 0.13
**Dépôt :** https://github.com/akretion/pyfrctc
**Rôle :** implémente le standard **AFNOR XP Z12-013** (API des Plateformes Agréées / PDP) : authentification OAuth2, requêtes d'annuaire (SIREN/SIRET), envoi/recherche de flux, génération des fichiers CDAR de cycle de vie. Utilisée par le module `l10n_fr_einvoicing`. Détail complet de l'API : [documentation-pyfrctc.md](./documentation-pyfrctc.md).

Dépendances (installées automatiquement par pip) : `lxml`, `python-dateutil`, `python-stdnum>=1.20`, `pytz`, `requests`, `requests-oauthlib`. Nécessite Python ≥ 3.9.

Comme `factur-x`, `pyfrctc` 0.13 ne dépend plus de `saxonche` : la validation Schematron des fichiers **CDAR** (fonction `check_cdar_schematron`) passe par une requête HTTP vers [Saxon Server](./saxon-server.md) (même changement, motivé par le même bug GraalVM : https://github.com/akretion/pyfrctc/issues/3). Rien à installer côté `saxonche` pour cette lib.

## Installation

Disponible sur PyPI depuis la version 0.13 (avant ça, install directe depuis GitHub). Même convention que pour [factur-x](./lib-factur-x.md) sur nos VPS Odoo : pas de venv, install system-wide en root.

```bash
pip install --break-system-packages pyfrctc==0.13
```

Pour minimiser ce qui est géré par pip plutôt que par `apt` (plus propre à maintenir), installer d'abord via `apt` les dépendances disponibles dans les dépôts Debian, puis relancer l'install pip — les paquets déjà satisfaits par `apt` ne seront pas réinstallés par pip :

```bash
apt install python3-oauthlib python3-requests-oauthlib
pip install --break-system-packages pyfrctc==0.13
```

`python-stdnum` restera néanmoins géré par pip : la version Debian (1.18) est trop ancienne pour l'exigence de `pyfrctc` (`>=1.20`), pip doit donc en installer une plus récente quoi qu'il arrive.

## Vérifier ce qui est installé

```bash
pip3 show pyfrctc
```

## Sources

- [akretion.md](./akretion.md) — contexte de la réforme et versions utilisées
- [documentation-pyfrctc.md](./documentation-pyfrctc.md) — détail de l'API (annuaire, flux, CDAR)
- [lib-factur-x.md](./lib-factur-x.md) — lib complémentaire (génération Factur-X/UBL)
- [saxon-server.md](./saxon-server.md) — service externe requis pour la validation Schematron (Factur-X **et** CDAR)
