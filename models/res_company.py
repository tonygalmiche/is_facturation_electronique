# -*- coding: utf-8 -*-

from odoo import _, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    def _en16931_checks(self):
        # Réimplémentation de account_invoice_en16931.ResCompany._en16931_checks()
        # sans le test sur la précision décimale "Product Unit of Measure" (qui
        # doit être <= 4 dans l'implémentation d'origine).
        #
        # Ce test est un blocage global (pas lié à une facture précise) sur un
        # réglage système qu'on ne veut pas abaisser (besoin métier de plus de
        # précision en interne sur les quantités). Le retirer ici n'a pas
        # d'impact sur la conformité EN16931 du document envoyé : la
        # génération du XML Factur-X/UBL arrondit de toute façon les
        # quantités à 4 décimales (imposé par la norme), que ce contrôle soit
        # actif ou non — il ne fait qu'empêcher par anticipation la
        # confirmation de facture, sans rapport avec la précision réellement
        # utilisée sur le document légal généré.
        sale_taxes = self.env["account.tax"].search(
            [("company_id", "=", self.id), ("type_tax_use", "=", "sale")]
        )
        errors = []
        for tax in sale_taxes:
            errors += tax._en16931_check_sale_tax()
        dpo = self.env["decimal.precision"]
        price_prec = dpo.precision_get("Product Price")
        if price_prec > 4:
            errors.append(
                _(
                    "La précision décimale du prix est de %s. Pour EN16931, "
                    "la valeur maximale est de 4.",
                    price_prec,
                )
            )
        if errors:
            raise UserError(
                _(
                    "Les erreurs suivantes ont été détectées sur la société "
                    "%(company)s qui bloquent la facturation électronique "
                    "EN16931 :\n%(err_msg)s",
                    company=self.display_name,
                    err_msg="\n".join([f"- {error}" for error in errors]),
                )
            )
