# Module `l10n_fr_siret`

**Source :** OCA / l10n-france  
**Version :** 18.0.1.3.0  
**Dépendances :** `l10n_fr`, `base_view_inheritance_extension`, `python-stdnum >= 1.18`

---

## Contexte : champ SIRET natif dans Odoo

Le module officiel `l10n_fr` (inclus dans Odoo) ajoute déjà un champ `siret` minimal :

| Modèle | Champ | Type | Remarque |
|--------|-------|------|----------|
| `res.partner` | `siret` | Char(14) | Pas de validation, pas de décomposition |
| `res.company` | `siret` | Char(14, related) | Lié à `partner_id.siret`, lecture/écriture |

Il n'y a **pas de champ `siren`, pas de champ `nic`**, pas de validation du checksum Luhn, pas de détection de doublons, ni de méthodes utilitaires.

Le module `l10n_fr_siret` **remplace et enrichit** cette approche minimaliste.

---

## Objectif

Ajoute la gestion complète des numéros d'identité des entreprises françaises sur les partenaires et les sociétés :

- Champs **SIREN** (9 chiffres, identifie l'entreprise), **NIC** (5 chiffres, identifie le site) et **SIRET** (SIREN + NIC)
- **Validation** du checksum Luhn sur le SIRET
- **Décomposition automatique** : saisir le SIRET entier décompose automatiquement SIREN et NIC
- **Détection de doublons** : alerte visuelle si deux partenaires partagent le même SIREN
- Support **multi-sites** : le SIREN est un champ commercial (partagé entre les contacts d'une même entreprise), le NIC est un champ d'adresse (spécifique par site)
- Hook de migration : décompose les anciens SIRET en SIREN + NIC à l'installation

---

## Nouveaux Menus

Aucun menu ajouté. Les champs sont intégrés directement dans les formulaires existants des partenaires et sociétés.

---

## Nouveaux Champs

### Modèle `res.partner` (Partenaires)

| Champ | Type | Description |
|-------|------|-------------|
| `siren` | Char(9) | Numéro SIREN — identifie l'entreprise (champ commercial, partagé entre contacts) |
| `nic` | Char(5) | Numéro NIC — identifie le site (champ d'adresse, spécifique par établissement) |
| `siret` | Char(14) | SIRET calculé (SIREN + NIC) — saisie directe possible, décomposition automatique |
| `parent_is_company` | Boolean (calculé) | Vrai si le contact parent est une entreprise |
| `same_siren_partner_ids` | Many2many (calculé) | Partenaires ayant le même SIREN (utilisé pour l'alerte de doublon) |
| `is_france_country` | Boolean (calculé) | Vrai si le pays du partenaire est la France |

**Comportements :**
- Le champ `siret` est en **lecture seule** si le partenaire a un parent (seul le NIC est modifiable dans ce cas)
- Une **bannière d'avertissement** s'affiche si d'autres partenaires ont le même SIREN
- Les champs SIREN/NIC/SIRET sont invisibles pour les partenaires non-français
- Une **contrainte de validation** vérifie le format et le checksum à la sauvegarde

### Modèle `res.company` (Sociétés)

| Champ | Type | Description |
|-------|------|-------------|
| `siren` | Char | SIREN de la société (stocké, modifiable, lié à `partner_id.siren`) |
| `nic` | Char | NIC de la société (stocké, modifiable, lié à `partner_id.nic`) |
| `siret` | Char | SIRET de la société (lecture seule, calculé depuis SIREN + NIC) |

---

## Installation

Dépôt `OCA/l10n-france`. Ne pas oublier la dépendance [base_view_inheritance_extension.md](./base_view_inheritance_extension.md) (autre dépôt, `OCA/server-tools`).

```bash
cd /tmp
git clone -b 18.0 --depth 1 https://github.com/OCA/l10n-france.git
mv l10n-france/l10n_fr_siret /media/sf_dev_odoo/18.0/facturation-electronique/
rm -rf l10n-france
```
