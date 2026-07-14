# -*- coding: utf-8 -*-

from odoo import models


class BusinessDocumentImport(models.AbstractModel):
    _inherit = "business.document.import"

    def _hook_match_partner(self, partner_dict, chatter_msg, domain, order):
        # l10n_fr_einvoicing ne fournit que 'siren'/'siret' dans partner_dict
        # (fr_einvoicing_flow.py:_match_partner_from_event), or la méthode
        # générique OCA ne sait matcher que sur ref/vat/contact/nom/website
        # (cf. is_facturation_electronique/documentation/import-depuis-super-pdp.md).
        siren = partner_dict.get("siren")
        if siren:
            partner = self.env["res.partner"].search(
                domain + [("siren", "=", siren)], limit=1, order=order
            )
            if partner:
                return partner
        return super()._hook_match_partner(partner_dict, chatter_msg, domain, order)
