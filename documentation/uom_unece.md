# Module `uom_unece`

**Dépôt :** https://github.com/OCA/community-data-files (sous-module `uom_unece`, branche `18.0`)
**Auteur :** Akretion France / OCA
**Licence :** AGPL-3
**Statut :** Production/Stable
**Dépendances :** `uom` (module natif Odoo)

---

## Objectif

Ajoute la codification **UNECE des unités de mesure** sur le modèle natif `uom.uom` (les unités de vente/achat d'Odoo). Nécessaire pour que la quantité facturée (BT-129/BT-130 de la norme EN16931) exprime son unité avec un code standardisé, reconnu par les schématrons Factur-X/UBL.

C'est une dépendance de [account_invoice_en16931.md](./account_invoice_en16931.md).

## Ce que fait le code concrètement

⚠️ Contrairement à `account_tax_unece` et `account_payment_unece`, ce module **ne dépend pas de `base_unece`** et n'utilise pas le modèle générique `unece.code.list` (cf. [base_unece.md](./base_unece.md)). Il ajoute directement un champ texte simple sur `uom.uom` :

```python
class UomUom(models.Model):
    _inherit = "uom.uom"
    unece_code = fields.Char(string="UNECE Code")
```

Le fichier `data/unece.xml` pré-remplit ce champ sur les unités de mesure standards déjà fournies par Odoo (ex. `uom.product_uom_unit` → code `C62`, `uom.product_uom_dozen` → code `DPC`, `uom.product_uom_day` → code `DAY`, `uom.product_uom_hour` → code `HUR`...), avec parfois des commentaires justifiant le choix d'un code UNECE plutôt qu'un autre proche (ex. `DPC` "dozen piece" préféré à `DZN` "dozen" pour rester dans la bonne catégorie UNECE).

## Installation

```bash
cd /tmp
git clone -b 18.0 --depth 1 https://github.com/OCA/community-data-files.git
mv community-data-files/uom_unece /media/sf_dev_odoo/18.0/facturation-electronique/
rm -rf community-data-files
```

## Sources

- Module : https://github.com/OCA/community-data-files/tree/18.0/uom_unece
- Module dépendant : [account_invoice_en16931.md](./account_invoice_en16931.md)
