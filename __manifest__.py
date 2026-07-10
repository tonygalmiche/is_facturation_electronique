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
