# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_force_saxon_validation = fields.Boolean(
        string="Obliger la validation Schematron Saxon à la confirmation de la facture",
        config_parameter="is_facturation_electronique.force_saxon_validation",
    )
