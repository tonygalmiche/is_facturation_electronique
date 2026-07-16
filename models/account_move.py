# -*- coding: utf-8 -*-

from facturx import xml_check_schematron

from odoo import models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"




    # def _prepare_bg23(self, base_lines, speedy):
    #     # Correctif pour account_invoice_en16931 (au 2026-07-13, commit 49e17e8) :
    #     # les clés lues ci-dessous étaient "target_base_amount_currency",
    #     # "target_tax_amount_currency" et "target_tax_amount", mais la méthode
    #     # du cœur Odoo 18 account.tax._aggregate_base_lines_aggregated_values()
    #     # renvoie "base_amount_currency", "tax_amount_currency" et "tax_amount"
    #     # (sans le préfixe "target_"). Les mauvaises clés retombaient
    #     # silencieusement à 0 via .get(clé, 0), donc BT-116/BT-117 (base/montant
    #     # TVA) étaient toujours à 0.00, faisant échouer les règles schematron
    #     # BR-FXEXT-S08b/S-08ini/S-08rev/CO-15.
    #     # Copie complète de la méthode d'origine, seuls les noms de clés changent.
    #     self.ensure_one()
    #     bt110 = bt111 = 0.0
    #     bg23 = []
    #     if speedy["company_no_vat_taxes"]:
    #         vat_dict = speedy["vat_info4company_no_vat_taxes"]
    #         bg23.append(
    #             {
    #                 "BT-118": vat_dict["categ_code"],
    #                 "BT-117-1": self.currency_id.name,  # for UBL
    #                 "BT-116-1": self.currency_id.name,  # for UBL
    #                 "BT-116": self.currency_id._en16931_format(
    #                     self.amount_total
    #                 ),  # base
    #                 "BT-117": self.currency_id._en16931_format(0),  # amount
    #                 "BT-121": vat_dict["vatex_code"],
    #                 "BT-120": vat_dict["vatex_label"],
    #             }
    #         )
    #         return bg23, bt110, bt111
    #     tax_obj = self.env["account.tax"]
    #     tax_amls = self.line_ids.filtered(lambda x: x.tax_repartition_line_id)
    #     tax_lines = [self._prepare_tax_line_for_taxes_computation(x) for x in tax_amls]
    #     tax_obj._round_base_lines_tax_details(
    #         base_lines, self.company_id, tax_lines=tax_lines
    #     )

    #     def grouping_function(base_line, tax_data):
    #         tax = tax_data["tax"]
    #         grouping_key = {
    #             "unece_type_code": tax.unece_type_code,
    #             "unece_categ_code": tax.unece_categ_code,
    #             "rate_int": int(round(tax.amount * 1000)),
    #             "vatex_code": tax.unece_vatex_code,
    #             "vatex_label": tax.unece_vatex_id.name,
    #         }
    #         return grouping_key

    #     base_lines_aggregated_values = tax_obj._aggregate_base_lines_tax_details(
    #         base_lines, grouping_function
    #     )
    #     values_per_grouping_key = tax_obj._aggregate_base_lines_aggregated_values(
    #         base_lines_aggregated_values
    #     )
    #     for tax_dict, tax_vals in values_per_grouping_key.items():
    #         if tax_dict["unece_type_code"] == "VAT":
    #             bt110 += tax_vals.get("tax_amount_currency", 0)
    #             bt111 += tax_vals.get("tax_amount", 0)
    #             bg23.append(
    #                 {
    #                     "BT-116": self.currency_id._en16931_format(
    #                         tax_vals.get("base_amount_currency", 0)
    #                     ),
    #                     "BT-116-1": self.currency_id.name,
    #                     "BT-117": self.currency_id._en16931_format(
    #                         tax_vals.get("tax_amount_currency", 0)
    #                     ),
    #                     "BT-117-1": self.currency_id.name,
    #                     "BT-118": tax_dict["unece_categ_code"],
    #                     "BT-119": "%.2f" % (tax_dict["rate_int"] / 1000),  # rate
    #                     "BT-120": tax_dict["vatex_label"],
    #                     "BT-121": tax_dict["vatex_code"],
    #                 }
    #             )
    #     return bg23, bt110, bt111

    def generate_en16931_xml(self, flavor2level, pdf_invoice_bin=False):
        # Si is_facturation_electronique.force_saxon_validation est actif,
        # le XML est envoyé une seconde fois à Saxon Server ci-dessous (en plus
        # de l'appel déjà fait dans super()) pour pouvoir bloquer la facture
        # avec raise_if_http_error=True (cf. commentaire plus bas).
        flavor2xmlbytes = super().generate_en16931_xml(
            flavor2level, pdf_invoice_bin=pdf_invoice_bin
        )
        force_saxon_validation = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("is_facturation_electronique.force_saxon_validation")
        )
        if force_saxon_validation:
            check_schematron = "base"
            if hasattr(
                self, "fr_directory_partner_entity_type"
            ) and self.fr_directory_company_entity_type in (
                "private",
                "private_inactive",
            ):
                if self.fr_directory_partner_entity_type in (
                    "private",
                    "private_inactive",
                ):
                    check_schematron = "fr-ctc"
                elif self.fr_directory_partner_entity_type == "public":
                    check_schematron = "fr-chorus"
            saxon_server_url = self._get_specific_saxon_server_url()
            saxon_server_codedb_dir = self._get_saxon_server_codedb_dir()
            # generate_en16931_xml() ci-dessus a déjà exécuté ce même contrôle
            # schematron une fois par flavor, mais en ignorant silencieusement
            # les échecs de communication (raise_if_http_error=False, câblé en
            # dur dans la lib facturx et non surchargeable depuis Odoo). On le
            # relance ici avec raise_if_http_error=True pour bloquer réellement
            # la facture quand Saxon Server est injoignable (un échec de
            # validation réel, c'est-à-dire un fichier qui échoue vraiment au
            # schematron, lève déjà une erreur de son côté).
            for flavor, xml_bytes in flavor2xmlbytes.items():
                try:
                    xml_check_schematron(
                        xml_bytes,
                        flavor=flavor,
                        level=flavor2level[flavor],
                        check_option=check_schematron,
                        saxon_server_url=saxon_server_url,
                        saxon_server_codedb_dir=saxon_server_codedb_dir,
                        raise_if_http_error=True,
                    )
                except Exception as err:
                    raise UserError(
                        self.env._(
                            "Failed to validate the %(flavor)s XML file against "
                            "the Saxon schematron server. Error: %(err)s",
                            flavor=flavor,
                            err=str(err),
                        )
                    ) from err
        return flavor2xmlbytes
