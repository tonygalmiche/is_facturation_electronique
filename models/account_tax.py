# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import UserError

# Catégories UNECE (UNCL5305) définies par le module OCA account_tax_unece
CATEG_XMLIDS = {
    "S": "account_tax_unece.tax_categ_s",  # Standard rate
    "AA": "account_tax_unece.tax_categ_aa",  # Lower rate (taux réduit)
    "E": "account_tax_unece.tax_categ_e",  # Exempt from tax (exonération à vérifier)
    "G": "account_tax_unece.tax_categ_g",  # Free export item, tax not charged
    "K": "account_tax_unece.tax_categ_k",  # VAT exempt intra-community supply
    "AE": "account_tax_unece.tax_categ_ae",  # VAT Reverse Charge (autoliquidation)
    "O": "account_tax_unece.tax_categ_o",  # Services outside scope of tax
}
# Catégories dont le motif d'exonération VATEX n'est pas déduit automatiquement
# par account_tax_unece (cf. _compute_unece_vatex_id, qui ne gère que K et G)
CATEG_TO_REVIEW = ("E", "O")


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _guess_unece_categ_code(self):
        # Déduit la catégorie UNECE (UNCL5305) à partir du nom et du taux de
        # la taxe, sur la base des intitulés du plan comptable français.
        self.ensure_one()
        if self.amount_type != "percent":
            return False
        name = (self.name or "").lower()
        is_intracom = "intracommunaut" in name
        # Autoliquidation sur acquisition intracommunautaire (achat) : taxe
        # "due" et taxe "déductible" associée, quel que soit le taux.
        if self.type_tax_use == "purchase" and is_intracom:
            return "AE"
        if self.amount == 0:
            if is_intracom:
                return "K"
            if "export" in name:
                return "G"
            if "hors champ" in name or "non imposable" in name:
                return "O"
            return "E"
        # Taux standard actuel (20%) et ancien taux standard (19.6%, avant 2014)
        if abs(self.amount - 20) < 0.01 or abs(self.amount - 19.6) < 0.01:
            return "S"
        return "AA"

    def action_set_unece_codes(self):
        if not self:
            raise UserError(
                self.env._("Sélectionnez au moins une taxe avant de lancer cette action.")
            )
        vat_type = self.env.ref("account_tax_unece.tax_type_vat")
        updated = 0
        already_set = 0
        to_review = []
        for tax in self:
            if tax.unece_type_id and tax.unece_categ_id:
                already_set += 1
                continue
            vals = {}
            if not tax.unece_type_id:
                vals["unece_type_id"] = vat_type.id
            if not tax.unece_categ_id:
                categ_code = tax._guess_unece_categ_code()
                if categ_code:
                    vals["unece_categ_id"] = self.env.ref(
                        CATEG_XMLIDS[categ_code]
                    ).id
                    if categ_code in CATEG_TO_REVIEW:
                        to_review.append("%s (%s)" % (tax.name, categ_code))
            if vals:
                tax.write(vals)
                updated += 1

        message = self.env._(
            "%(updated)d taxe(s) mise(s) à jour, %(already_set)d déjà renseignée(s).",
            updated=updated,
            already_set=already_set,
        )
        if to_review:
            message += "\n" + self.env._(
                "A vérifier manuellement (catégorie et motif d'exonération VATEX) : %(taxes)s",
                taxes=", ".join(to_review),
            )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("Codes UNECE des taxes"),
                "message": message,
                "sticky": bool(to_review),
                "type": "success",
                # Recharge la vue courante pour afficher les valeurs mises à jour
                "next": {"type": "ir.actions.client", "tag": "soft_reload"},
            },
        }
