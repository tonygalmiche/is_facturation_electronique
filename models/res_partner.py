# -*- coding: utf-8 -*-

from odoo import _, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_siren(self, raise_if_none=False):
        # Fallback pour les bacs à sable (ex: Super PDP) qui utilisent des SIREN
        # fictifs ne respectant pas la clé de Luhn. Utilisé à la fois par le
        # bouton "Directory Sync" et par la validation de facture
        # (_fr_ctc_is_vat_registered, appelée depuis account.move._post()).
        # La validation normale (super()) reste prioritaire ; on n'accepte le
        # SIREN stocké tel quel que si elle n'a rien trouvé.
        self.ensure_one()
        siren_value = super()._get_siren(raise_if_none=False)
        if not siren_value:
            partner = self.parent_id or self
            siren_value = partner.siren or False
        if not siren_value and raise_if_none:
            raise UserError(
                _(
                    "SIREN is not set on partner '%(partner)s'.",
                    partner=(self.parent_id or self).display_name,
                )
            )
        return siren_value
