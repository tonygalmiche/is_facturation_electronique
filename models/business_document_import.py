# -*- coding: utf-8 -*-

# Ce fichier étend business.document.import (modèle abstrait fourni par
# base_business_document_import), utilisé uniquement pour l'import des
# factures fournisseur reçues via Super PDP (cas 3, cf.
# is_facturation_electronique/documentation/installation.md). Désactivé tant
# que base_business_document_import n'est pas dans les depends du manifest
# (cas 1 actif actuellement) : sans lui, business.document.import n'existe
# pas dans le registre Odoo et le _inherit ci-dessous ferait planter le
# chargement du module. Décommenter en même temps que le cas 3.

# from odoo import models
#
#
# class BusinessDocumentImport(models.AbstractModel):
#     _inherit = "business.document.import"
#
#     def _hook_match_partner(self, partner_dict, chatter_msg, domain, order):
#         # Fait matcher le partenaire fournisseur par SIREN avant de retomber
#         # sur le matching générique OCA (ref/vat/contact/nom/website) :
#         # l10n_fr_einvoicing ne fournit que 'siren'/'siret' dans partner_dict
#         # (fr_einvoicing_flow.py:_match_partner_from_event), or la méthode
#         # générique OCA ne sait matcher que sur ref/vat/contact/nom/website
#         # (cf. is_facturation_electronique/documentation/import-depuis-super-pdp.md).
#         siren = partner_dict.get("siren")
#         if siren:
#             partner = self.env["res.partner"].search(
#                 domain + [("siren", "=", siren)], limit=1, order=order
#             )
#             if partner:
#                 return partner
#         return super()._hook_match_partner(partner_dict, chatter_msg, domain, order)
