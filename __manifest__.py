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

        'l10n_fr_einvoicing',              # Facturation electronique Akretion
        'l10n_fr_siret',                   # Dépendance OCA Akretion
        'l10n_fr_siret_account',           # Dépendance OCA Akretion
        'base_view_inheritance_extension', # Dépendance OCA Akretion


        'base_unece',
        'account_tax_unece',
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
