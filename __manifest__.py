# -*- coding: utf-8 -*-
{
    'name'     : 'InfoSaône - Module Odoo 18 pour Facturation électronique',
    'version'  : '18.0.0.1',
    'author'   : 'InfoSaône',
    'category' : 'InfoSaône',
    'description': """
InfoSaône - Module Odoo 18 pour Facturation électronique
========================================================
""",
    'maintainer' : 'InfoSaône',
    'website'    : 'http://www.infosaone.com',
    'depends'    : [
        'base',
        'account',                         # Facturation de base Odoo

        'l10n_fr_einvoicing',               # Akretion - facturation électronique française (CTC)
        'base_business_document_import',    # OCA - modèle business.document.import, requis par l10n_fr_einvoicing (import Super PDP)
        'account_invoice_import',           # OCA - import factures fournisseur PDF/XML, requis par l10n_fr_einvoicing_import
        'base_facturx',                     # OCA - socle technique requis par account_invoice_import_facturx
        'account_invoice_import_facturx',   # OCA - parsing du XML CII/Factur-X embarqué dans le PDF fournisseur
        'l10n_fr_einvoicing_import',        # Akretion - implémente réellement l'import des factures fournisseur Super PDP
        'l10n_fr_siret',                    # OCA - SIREN/NIC/SIRET sur partenaires
        'l10n_fr_siret_account',            # OCA - lien SIRET / comptabilité française
        'base_view_inheritance_extension',  # OCA - dépendance technique (héritage de vues)

        'l10n_fr_account_invoice_en16931',  # Akretion - surcouche France de la génération EN16931
        'account_invoice_en16931',          # Akretion - génération Factur-X/UBL EN16931, config Saxon Server

        'account_tax_unece',                # OCA - codes UNECE taxes + motifs d'exonération VATEX
        'base_unece',                       # OCA - modèle générique des nomenclatures UNECE
        'uom_unece',                        # OCA - codes UNECE unités de mesure
        'account_payment_unece',            # OCA - codes UNECE moyens de paiement
        'account_payment_method_base',      # OCA - vues manquantes account.payment.method
        'intrastat_base',                   # OCA - socle des déclarations Intrastat
    ],
    'data' : [
        'views/menu.xml',
        'views/res_config_settings_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'is_facturation_electronique/static/src/scss/style.scss',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
