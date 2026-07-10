## Répositories Github Akretion pour Facturation Electronique


Lib python pyfrctc : https://github.com/akretion/pyfrctc
Lib factur-x : https://github.com/akretion/factur-x

nouveaux modules dédiés : https://github.com/akretion/fr-einvoicing
import factures Factur-X et UBL : https://github.com/OCA/edi
données UNECE : https://github.com/OCA/community-data-files/ (je ne prévois pas de changement)
La génération du XML Factur-X sera peut-être déplacé sur la lib factur-x
Depend de :


PR v18 sur l10n_fr_siret https://github.com/OCA/l10n-france/pull/768 : ajout des méthodes
_get_siren() et _get_siret() comme en v19
temporaire : account_invoice_facturx
https://github.com/akretion/edi/tree/18-account_invoice_facturx-ctc
temporaire : l10n_fr_account_invoice_facturx
https://github.com/akretion/l10n-france/tree/18-l10n_fr_account_invoice_facturx-ctc



## Installation de pyfrctc
```bash
pip install --user --break-system-packages git+https://github.com/akretion/pyfrctc.git
```


## Installation de factur-x (Akretion)
```bash
pip install --user --break-system-packages git+https://github.com/akretion/factur-x
```

> **Warning PATH :** après installation, un avertissement indique que les scripts (`facturx-pdfgen`, `facturx-pdfextractxml`, `facturx-xmlcheck`) sont dans `/home/odoo/.local/bin` qui n'est pas dans le PATH.
> Cela n'affecte **pas** l'utilisation de la lib dans Odoo (`import facturx` fonctionne normalement).
> Pour utiliser ces scripts en ligne de commande, ajouter dans `~/.bashrc` :
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```

## Installation des modules Odoo Akretion
```bash
pip install --user --break-system-packages packaging
git clone --branch 18.0 --single-branch https://github.com/OCA/l10n-france.git
git clone --branch 18.0 --single-branch https://github.com/OCA/server-tools.git
git clone https://github.com/akretion/fr-einvoicing.git

```

# Module Akretion pour facturation electronique
```
l10n_fr_einvoicing
l10n_fr_siret
l10n_fr_siret_account
base_view_inheritance_extension
```


