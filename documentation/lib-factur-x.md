# Lib Python `factur-x`

**Paquet PyPI :** `factur-x`
**Version utilisée par la réforme (cf. [akretion.md](./akretion.md)) :** 6.1
**Dépôt :** https://github.com/akretion/factur-x
**Rôle :** génération et validation des factures Factur-X / UBL / CII (CTC), utilisée par les modules `l10n_fr_einvoicing` / `account_invoice_en16931`. Depuis la réécriture (v6+), ne dépend plus de `saxonche` : la validation Schematron passe par [Saxon Server](./saxon-server.md), un service HTTP externe.

Dépendances (installées automatiquement par pip) : `lxml`, `pypdf>=5.3.0`, `python-stdnum`, `requests`. Nécessite Python ≥ 3.9.

## Installation

Sur Debian, `pip install` direct échoue avec `externally-managed-environment` (PEP 668) : le Python système est protégé contre les installs pip non maîtrisés par `apt`.

**Convention retenue sur nos VPS Odoo : pas de venv, install system-wide avec `--break-system-packages`.** Cohérent avec le fait qu'`odoo-bin` (`#!/usr/bin/env python3`) tourne directement sur le Python système, et que d'autres libs (dont une ancienne version de `factur-x`) y sont déjà installées de cette façon.

```bash
pip install --break-system-packages factur-x==6.1
```

- À exécuter en tant que **root** (ex. `su -` ou session root) : le dossier `/usr/local/lib/python3.X/dist-packages/` appartient à `root`, l'utilisateur `odoo` n'a pas les droits d'écriture dessus.
- Pas besoin de désinstaller l'ancienne version avant : `pip install` remplace automatiquement les fichiers d'une version précédente du même paquet.
- Risque limité de cette approche (raison du warning Debian) : un futur `apt upgrade` pourrait théoriquement entrer en conflit si Debian empaquetait aussi `factur-x` — non applicable ici, ce paquet n'est pas dans les dépôts Debian/Ubuntu.

## Vérifier ce qui est installé

```bash
# Version installée system-wide (utilisée par odoo-bin) :
pip3 show factur-x

# Liste complète des paquets Python system-wide :
pip3 list
```

`pip list` seul ne distingue pas ce qui vient de `pip` ou d'`apt`. Sur Debian, les deux sont bien séparés par emplacement :

- `apt` installe dans `/usr/lib/python3/dist-packages/`
- `pip` system-wide (`--break-system-packages`) installe dans `/usr/local/lib/python3.X/dist-packages/`

```bash
pip3 show factur-x | grep Location   # emplacement du paquet
dpkg -l | grep python3-lxml          # présent uniquement si installé via apt
```



## Sources

- [akretion.md](./akretion.md) — annonce de la réécriture Factur-X/UBL et passage à Saxon Server
- [saxon-server.md](./saxon-server.md) — le service externe requis pour la validation Schematron
- [documentation-pyfrctc.md](./documentation-pyfrctc.md) — lib `pyfrctc`, dépendance complémentaire (annuaire, événements AFNOR)
