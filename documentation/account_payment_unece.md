# Module `account_payment_unece`

**Dépôt :** https://github.com/OCA/community-data-files (sous-module `account_payment_unece`, branche `18.0`)
**Auteur :** Akretion France / OCA
**Licence :** AGPL-3
**Dépendances :** `account_payment_method_base` (dans OCA/account-payment), `base_unece`

---

## Objectif

Ajoute un champ **UNECE Payment Mean** sur les moyens de paiement (`account.payment.method`), pour coder les moyens de paiement selon la nomenclature UNECE **DataElement 4461** (cf. [base_unece.md](./base_unece.md) pour le fonctionnement général des listes UNECE).

C'est une dépendance de [account_invoice_en16931](./account_invoice_en16931.md) : la norme EN16931 exige que le moyen de paiement indiqué sur la facture électronique (BT-81, "Payment means type code") soit exprimé avec un code standardisé — ce module fournit ce référentiel de codes et le lien entre eux et les moyens de paiement Odoo.

## Ce que fait le code concrètement

Sur le modèle `account.payment.method` (déjà existant dans Odoo), ajoute :

```python
unece_id = fields.Many2one(
    "unece.code.list",
    domain=[("type", "=", "payment_means")],
)
unece_code = fields.Char(related="unece_id.code", store=True)
```

Le module fournit aussi les **données** :

- `data/unece.xml` — la liste des codes UNECE de type `payment_means` (chargée dans le modèle générique `unece.code.list` de `base_unece`)
- `data/account_payment_method.xml` — le rattachement des moyens de paiement standards d'Odoo (virement, prélèvement, chèque...) à leur code UNECE correspondant

## Installation

Le même principe que pour les autres modules `*_unece` : clone temporaire, on ne garde que le dossier du module.

```bash
cd /tmp
git clone -b 18.0 --depth 1 https://github.com/OCA/community-data-files.git
mv community-data-files/account_payment_unece /media/sf_dev_odoo/18.0/facturation-electronique/
rm -rf community-data-files
```

⚠️ Dépend aussi de `account_payment_method_base`, module d'un **autre dépôt OCA** : https://github.com/OCA/account-payment. À récupérer séparément si pas déjà présent.

## Sources

- Module : https://github.com/OCA/community-data-files/tree/18.0/account_payment_unece
- Dépendance technique : [base_unece.md](./base_unece.md)
- Module dépendant : [account_invoice_en16931.md](./account_invoice_en16931.md)
