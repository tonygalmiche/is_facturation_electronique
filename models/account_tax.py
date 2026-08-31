# -*- coding: utf-8 -*-

from odoo import _, models
from odoo.exceptions import UserError

# Catégories UNECE (UNCL5305) définies par le module OCA account_tax_unece
CATEG_XMLIDS = {
    "S": "account_tax_unece.tax_categ_s",  # Standard rate
    "E": "account_tax_unece.tax_categ_e",  # Exempt from tax (exonération à vérifier)
    "G": "account_tax_unece.tax_categ_g",  # Free export item, tax not charged
    "K": "account_tax_unece.tax_categ_k",  # VAT exempt intra-community supply
    "AE": "account_tax_unece.tax_categ_ae",  # VAT Reverse Charge (autoliquidation)
    "O": "account_tax_unece.tax_categ_o",  # Services outside scope of tax
}
# Catégories dont le motif d'exonération VATEX n'est pas déduit automatiquement
# par account_tax_unece (cf. _compute_unece_vatex_id, qui ne gère que K et G)
CATEG_TO_REVIEW = ("E", "O")
# Motif VATEX par défaut pour ces catégories : "Not subject to VAT" est le
# motif le plus générique de la liste UNCL5305 (aucun article de loi précis
# n'est deviné automatiquement) ; simple valeur de départ pour ne pas
# bloquer la validation, à corriger manuellement avec le vrai motif légal
# (la taxe reste signalée "à vérifier", cf. CATEG_TO_REVIEW ci-dessus).
DEFAULT_VATEX_XMLID = "account_tax_unece.tax_vatex_eu_o"


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
        if self.amount < 0:
            # Taux négatif (ex: "Escompte 0,5%") : ne correspond à aucune
            # catégorie EN16931 valide (S exige un taux strictement
            # positif) ; ce n'est pas un vrai taux de TVA au sens EN16931,
            # à configurer manuellement au cas par cas.
            return False
        # Tout taux de TVA positif est en catégorie EN16931/Peppol "S"
        # (Standard rated) : "AA" (Lower rate) n'est pas une catégorie
        # valide pour EN16931 (elle vient de la liste générale UNCL5305,
        # pas du sous-ensemble EN16931/Peppol), et il n'existe pas de
        # catégorie dédiée au "taux réduit" côté EN16931 — c'est le taux
        # lui-même (self.amount) qui porte l'information du pourcentage.
        return "S"

    def action_set_unece_codes(self):
        if not self:
            raise UserError(
                _("Sélectionnez au moins une taxe avant de lancer cette action.")
            )
        vat_type = self.env.ref("account_tax_unece.tax_type_vat")
        updated = 0
        already_set = 0
        to_review = []
        not_guessed = []
        archived = []
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
                        if not tax.unece_vatex_id:
                            vals["unece_vatex_id"] = self.env.ref(
                                DEFAULT_VATEX_XMLID
                            ).id
                        to_review.append("%s (%s)" % (tax.name, categ_code))
                elif tax.amount_type == "percent":
                    # Taux négatif (ex: "Escompte") : aucune catégorie EN16931
                    # valide n'existe pour ce cas (cf. _guess_unece_categ_code).
                    # Si la taxe n'est utilisée sur aucune ligne de facture,
                    # elle ne représente aucun risque à archiver : ça la sort
                    # du périmètre de la vérification EN16931 (qui ne porte
                    # que sur les taxes de vente actives), sans toucher à
                    # aucune donnée existante. Si elle est utilisée, on ne
                    # touche à rien : sa catégorie devra être configurée
                    # manuellement (le cas échéant après avoir revu la façon
                    # dont cet escompte est modélisé, cf. documentation).
                    if (
                        tax.amount < 0
                        and tax.type_tax_use == "sale"
                        and not self.env["account.move.line"].search(
                            [("tax_ids", "in", tax.id)], limit=1
                        )
                    ):
                        tax.active = False
                        archived.append(tax.name)
                    else:
                        not_guessed.append(tax.name)
            if vals:
                tax.write(vals)
                updated += 1

        message = _(
            "%(updated)d taxe(s) mise(s) à jour, %(already_set)d déjà renseignée(s).",
            updated=updated,
            already_set=already_set,
        )
        if to_review:
            message += "\n" + _(
                "A vérifier manuellement (catégorie et motif d'exonération VATEX) : %(taxes)s",
                taxes=", ".join(to_review),
            )
        if not_guessed:
            message += "\n" + _(
                "Catégorie non déduite automatiquement (taux négatif ou particulier), "
                "à configurer manuellement : %(taxes)s",
                taxes=", ".join(not_guessed),
            )
        if archived:
            message += "\n" + _(
                "Archivée(s) car taux négatif sans catégorie EN16931 valide et "
                "non utilisée(s) sur aucune facture : %(taxes)s",
                taxes=", ".join(archived),
            )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Codes UNECE des taxes"),
                "message": message,
                "sticky": bool(to_review or not_guessed or archived),
                "type": "success",
                # Recharge la vue courante pour afficher les valeurs mises à jour
                "next": {"type": "ir.actions.client", "tag": "soft_reload"},
            },
        }
