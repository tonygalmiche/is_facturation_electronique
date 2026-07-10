# Module `l10n_fr_siret_account`

**Source :** OCA / l10n-france  
**Version :** 18.0.1.1.0  
**Dépendances :** `l10n_fr_siret`, `l10n_fr_account`  
**Auto-install :** Oui (s'installe automatiquement quand les deux dépendances sont présentes)

---

## Objectif

Module **glue** (connecteur) entre `l10n_fr_siret` et le module de comptabilité `l10n_fr_account`. Il n'ajoute pas de fonctionnalité autonome mais remplit deux rôles :

1. **Audit trail (tracking)** : active le suivi des modifications sur les champs SIREN et NIC, ce qui inscrit un message dans le chatter du partenaire à chaque changement.
2. **Harmonisation des vues** : résout les conflits de visibilité du champ SIRET entre `l10n_fr_account` et `l10n_fr_siret` en appliquant une condition d'affichage cohérente.

---

## Nouveaux Menus

Aucun menu ajouté.

---

## Nouveaux Champs

Ce module **n'ajoute aucun nouveau champ**. Il modifie uniquement des attributs de champs existants.

### Modèle `res.partner` — modifications sur champs existants

| Champ | Modification apportée |
|-------|-----------------------|
| `siren` | Ajout de `tracking=50` → les modifications sont enregistrées dans le chatter |
| `nic` | Ajout de `tracking=51` → les modifications sont enregistrées dans le chatter |

### Vue `res.partner` — correction d'héritage

La vue héritée de `l10n_fr_account` est corrigée pour appliquer la même condition d'invisibilité que `l10n_fr_siret` sur le champ `siret` :

```
invisible: (not is_company and not parent_is_company) or not is_france_country
```

Cela évite que le champ SIRET apparaisse sur des partenaires non-français ou des contacts individuels dans le contexte comptable.
