# Module `l10n_fr_account_invoice_en16931`

**Auteur :** Akretion France
**Version :** 18.0.1.0.0
**Licence :** AGPL-3
**Dépôt :** https://github.com/akretion/fr-einvoicing (branche 18.0)
**Dépendances :** `account_invoice_en16931`, `l10n_fr_siret`

---

## Objectif

Surcouche **spécifique France** du module générique `account_invoice_en16931` (la ré-écriture de la génération Factur-X/UBL évoquée dans [akretion.md](./akretion.md)). Le module `l10n_fr_einvoicing` en dépend :

```
l10n_fr_einvoicing → l10n_fr_account_invoice_en16931 → account_invoice_en16931
```

Module très mince (un seul fichier `models/account_move.py`, pas de vues ni de données) : il **surcharge en Python** deux méthodes de génération du dictionnaire EN16931 pour y injecter des règles propres à la France.

## Ce que fait le code concrètement

### `_prepare_en16931_dict` — identifiants SIREN/SIRET

Ajoute les identifiants d'entreprise français dans le XML de la facture, **uniquement si la société est en France** (`company_id.is_france_country`) :

| Champ EN16931 | Contenu | Condition |
|---|---|---|
| `BT-30` / `BT-30-1` | SIREN du vendeur (schéma `0002`) | toujours |
| `BT-47` / `BT-47-1` | SIREN de l'acheteur (schéma `0002`) | toujours |
| `BT-29` (`0009`) | SIRET du vendeur | si secteur public (Chorus Pro) |
| `BT-46` (`0009`) | SIRET de l'acheteur | si secteur public (Chorus Pro) |
| `BT-46` (`0240`) / `BT-56-0` | Code de routage (annuaire e-invoicing) | si secteur public et ligne d'annuaire de type `routing_code` |

Le SIREN/SIRET est récupéré via les méthodes `_get_siren()` / `_get_siret()` (fournies par `l10n_fr_siret`, cf. [l10n_fr_siret.md](./l10n_fr_siret.md)). Le statut "secteur public" (`fr_directory_partner_entity_type == "public"`) vient du module `l10n_fr_einvoicing` (annuaire national).

### `_prepare_bg1` — mentions légales de paiement

Ajoute des mentions obligatoires en droit français sur les conditions de paiement, injectées dans le groupe de blocs BG1 :

- **Indemnité forfaitaire de recouvrement** (40 €) en cas de retard de paiement (`BT-21` = `PMT`)
- **Pénalités de retard** calculées sur 3x le taux d'intérêt légal (`BT-21` = `PMD`)
- **Pas d'escompte** pour paiement anticipé (`BT-21` = `AAB`)
- Mention `ADN` = `B2G` si le client est une entité publique

## Chaîne de dépendances complète

```
l10n_fr_account_invoice_en16931
├── l10n_fr_siret                    (SIREN/SIRET sur res.partner)
└── account_invoice_en16931          (génération EN16931 générique)
    ├── account_tax_unece            (+ base_unece, cf. account_tax_unece.md / base_unece.md)
    ├── uom_unece
    ├── account_payment_unece
    ├── base_vat
    └── intrastat_base
```

## Sources

- Module : https://github.com/akretion/fr-einvoicing/tree/18.0/l10n_fr_account_invoice_en16931
- Contexte de la réécriture : [akretion.md](./akretion.md)
- Module parent : [l10n_fr_einvoicing.md](./l10n_fr_einvoicing.md)
- Dépendances SIRET : [l10n_fr_siret.md](./l10n_fr_siret.md), [l10n_fr_siret_account.md](./l10n_fr_siret_account.md)
- Dépendances UNECE : [account_tax_unece.md](./account_tax_unece.md), [base_unece.md](./base_unece.md)
