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
apt install python3-pip
apt install python3-packaging
apt install unicode

su odoo
pip install --break-system-packages unidecode
pip install --break-system-packages factur-x
pip show factur-x
Version: 6.8
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

## Piège : Odoo peut voir une autre version que celle installée en root

`pip3 show factur-x` en root peut afficher la bonne version alors qu'**Odoo continue d'utiliser une ancienne version**. Cause : Odoo tourne sous l'utilisateur `odoo`, pas `root`. Si un `pip install --user` a été fait par le passé sous cet utilisateur, une copie existe dans `~/.local/lib/python3.X/site-packages/`, et **ce dossier est prioritaire dans `sys.path`** sur `/usr/local/lib/python3.X/dist-packages/` (où atterrit l'install system-wide en root). Résultat : Odoo importe la vieille copie utilisateur et ignore la mise à jour faite en root.

Symptôme observé : erreur `External dependency version mismatch: factur-x>=6.1 (installed: 4.4.dev2+...)` au moment d'installer/mettre à niveau un module, alors que `pip3 show factur-x` (en root) annonce bien 6.1.

Diagnostic — comparer la version vue par chaque utilisateur :

```bash
# En root :
python3 -c "import facturx; print(facturx.__file__)"

# En tant qu'utilisateur odoo (celui qui exécute réellement odoo-bin) :
su - odoo -c "python3 -c 'import facturx; print(facturx.__file__)'"
su - odoo -c "pip3 show factur-x"   # affiche la version vue par cet utilisateur

# Chercher toutes les copies présentes sur le système :
find / -iname 'facturx' -maxdepth 8 -type d 2>/dev/null
```

Si une copie existe dans `/home/odoo/.local/lib/python3.X/site-packages/facturx`, c'est elle qui est utilisée par Odoo, pas celle de `/usr/local/`. Correction : la supprimer (`pip3 uninstall --break-system-packages -y factur-x` **exécuté en tant qu'utilisateur `odoo`**, pas en root, pour cibler le bon emplacement) afin qu'Odoo retombe sur la version system-wide à jour.

## Extraire le XML d'une facture Factur-X (PDF)

Deux façons en ligne de commande :

**1. Avec `pdfdetach` (poppler-utils, le plus rapide, pas besoin de Python) :**

```bash
pdfdetach -list facture.pdf      # liste les pièces jointes du PDF (le XML est en général "factur-x.xml")
pdfdetach -saveall facture.pdf   # extrait toutes les pièces jointes dans le dossier courant
```

**2. Avec la lib `factur-x` elle-même (utilise la même logique d'extraction/autodétection qu'Odoo) :**

```bash
python3 -c "
from facturx import get_xml_from_pdf
xml_name, xml_bytes = get_xml_from_pdf('facture.pdf')
open(xml_name, 'wb').write(xml_bytes)
print(xml_name)
"
```

`get_xml_from_pdf` (`facturx.py:646`) gère l'autodétection Factur-X/UBL/ZUGFeRD et renvoie le nom de fichier attendu + le contenu XML.

## Sources

- [akretion.md](./akretion.md) — annonce de la réécriture Factur-X/UBL et passage à Saxon Server
- [saxon-server.md](./saxon-server.md) — le service externe requis pour la validation Schematron
- [lib-pyfrctc.md](./lib-pyfrctc.md) — lib `pyfrctc`, dépendance complémentaire (annuaire, événements AFNOR)
