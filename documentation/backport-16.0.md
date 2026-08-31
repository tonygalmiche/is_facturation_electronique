# Discussion du 31/08/2026 — Backport de la réforme en 16.0

Alexis de Lattre a commencé une discussion

Modules pour la réforme dispos en 16.0

Les modules pour la réforme de la facturation électronique sont maintenant disponibles pour Odoo 16 (avec quelques semaines de retard par rapport au planning que j'avais prévu...). Merci à tous ceux qui m'ont aidé dans ce backport (en particulier Nicolas Jeudy qui m'a beaucoup aidé dans les backports de PRs OCA).

Les modules sont disponibles ici :

https://github.com/akretion/fr-einvoicing/tree/16.0

Toutes les PRs OCA nécessaires ont été mergées, pour certaines il y a seulement quelques minutes. Il faut donc bien vous assurer que vous avez du code parfaitement à jour sur :

- OCA/community-data-files
- OCA/edi
- OCA/l10n-france
- OCA/account-financial-tools
- OCA/sale-workflow (si vous utilisez l10n_fr_einvoicing_sale)

Assurez-vous aussi que le code odoo que vous utilisez n'est pas trop vieux (ça m'est déjà arrivé de recevoir un bug report qui était en fait lié au fait que la personne utilisait du code Odoo très ancien ; c'était sur la 18.0, mais ça pourrait aussi arriver sur la 16.0).

Maintenant que le backport en 16.0 est réalisé, je vais maintenant me focaliser sur l'implémentation du e-reporting, tout en restant disponible pour corriger les bugs qui vous pourriez me remonter sur le volet e-invoicing. Une fois que le chantier du e-reporting sera finalisé, j'ai en projet de ré-écrire le parsing XML en UBL et CII/Factur-X : le but est de déplacer le code qui parse le XML dans la lib factur-x (comme c'est du code totalement indépendant de la version d'Odoo, c'est plus simple à maintenir s'il est dans une lib python), et qu'on puisse récupérer en sortie de la lib un dictionnaire python identique à celui qu'on utilise pour construire le XML UBL ou Factur-X avec la lib.

Alexis

Liens

- [GitHub - akretion/fr-einvoicing at 16.0](https://github.com/akretion/fr-einvoicing/tree/16.0)

---

## Vérification effectuée pour ce module (branche 16.0)

Suite à cette annonce, vérification des dépôts via l'API GitHub le 31/08/2026 :

### Dernier commit sur chaque dépôt (branche 16.0)

| Dépôt | Dernier commit (16.0) |
|---|---|
| `akretion/fr-einvoicing` | 2026-08-30 |
| `OCA/l10n-france` | 2026-08-20 |
| `OCA/edi` | 2026-08-18 |
| `OCA/account-financial-tools` | 2026-08-19 |
| `OCA/community-data-files` | 2026-08-11 |

Toutes les branches sont récentes, cohérent avec un backport tout juste finalisé.

### Cas 1 (actif dans le manifest de ce module)

Toutes les dépendances du Cas 1 (`account_invoice_en16931`, `l10n_fr_account_invoice_en16931`, `l10n_fr_siret`, `account_tax_unece`/`base_unece`/`uom_unece`/`account_payment_unece`, `intrastat_base`, `base_view_inheritance_extension`, `account_payment_method_base`) existent et sont à jour en 16.0. Rien à changer côté [`installation-modules-oca.sh`](./installation-modules-oca.sh) (déjà pointé sur 16.0, cf. commit d'adaptation du module).

### Correction : `l10n_fr_siret_account` n'est pas un vrai bloquant pour le Cas 2

Le commentaire du manifest de ce module (Cas 2, hérité tel quel de la branche 18.0) liste `l10n_fr_siret_account` comme dépendance. Ce module **n'existe pas** en branche 16.0 de `OCA/l10n-france` (vérifié via l'API `git/trees`, pas seulement via l'API `contents` qui peut être trompeuse). Cependant, en lisant le `__manifest__.py` réel de `l10n_fr_einvoicing` (identique sur 16.0 et 18.0) :

```python
"depends": [
    "l10n_fr_account_invoice_en16931",
],
```

`l10n_fr_einvoicing` ne dépend en réalité **pas** de `l10n_fr_siret_account` — ce dernier ne sert qu'à un usage annexe (export SIRET pour l'affacturage, cf. [OCA/l10n-france#782](https://github.com/OCA/l10n-france/pull/782)) et n'a jamais été backporté en 16.0 (pas de PR de backport trouvée). Ce n'est donc pas une régression spécifique à la 16.0 : le même écart entre le commentaire du manifest et les dépendances réelles existe déjà sur la branche 18.0.

**Conclusion :** le Cas 1 (actif) est prêt et à jour sur Odoo 16. Le Cas 2/3 (commentés, non activés) restent utilisables en théorie, avec la même réserve sur `l10n_fr_siret_account` que sur la branche 18.0 — pas de blocage propre à ce backport 16.0.

### Correctif : dépendances qui diffèrent entre 16.0 et 18.0

Le script a échoué à l'exécution (`account_payment_method_base introuvable`) : ce module n'existe pas en 16.0. En comparant les `depends` réels des modules entre 16.0 et 18.0, 3 différences propres à la 16.0 :

- `account_payment_unece` dépend de **`account_payment_mode`** (OCA/bank-payment) au lieu de `account_payment_method_base`.
- `account_invoice_en16931` dépend en plus de **`account_payment_partner`** (OCA/bank-payment).
- `base_business_document_import` dépend en plus de **`pdf_helper`** (OCA/edi).

Corrigé dans `__manifest__.py`, `installation-modules-oca.sh`, `last_update.sh` et `README.md`.

### Code Odoo 16 trop ancien

Rencontré aussi : l'action serveur "Renseigner les codes UNECE" (`account_tax.py`) plantait côté JS avec `KeyNotFoundError: Cannot find soft_reload in this registry!` — ce tag client existe pourtant bien dans le code source d'Odoo 16 (`addons/web/static/src/webclient/actions/client_actions.js`), mais pas dans les assets JS compilés de cette instance, preuve d'un commit Odoo trop ancien dans la branche 16.0. Résolu par une mise à jour du code Odoo 16 (`git pull`), sans toucher au module. Confirme l'avertissement d'Alexis de Lattre : "assurez-vous aussi que le code odoo que vous utilisez n'est pas trop vieux".
