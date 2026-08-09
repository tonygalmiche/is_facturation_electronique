# Problème d'installation du module uom_unece (02/08/2026)

## Symptôme

Lors de l'installation du module `uom_unece` (OCA, dépendance liée à la facturation électronique), l'installation plante avec :

```
odoo.tools.convert.ParseError: while parsing .../uom_unece/data/unece.xml:85, somewhere inside
<record id="uom.product_uom_qt" model="uom.uom">
    <field name="unece_code">QT</field>
</record>
```

Le `ParseError` d'Odoo n'affiche pas la vraie cause (il masque l'exception d'origine). En creusant dans la stacktrace complète, l'erreur réelle est :

```
Exception: Cannot update missing record 'uom.product_uom_qt'
```

## Cause réelle

Ces bases de données (`coheliance18`, `coheliance-formation18`) ont été migrées d'Odoo 14 vers Odoo 18. Le fichier `uom/data/uom_data.xml` du module core `uom` est chargé en `noupdate="1"` : ses enregistrements ne sont créés qu'à la toute première installation du module, jamais recréés lors d'une mise à jour.

Résultat de la migration 14 → 18 :

- la table `uom_uom` contient toujours les **22 unités** de l'époque Odoo 14 (pas de minute, millimètre, m², yard, ft², etc. ajoutés depuis) ;
- mais la table `ir_model_data` a été mise à jour avec le mapping **Odoo 18** (26 unités, 6 catégories) sans jamais recréer les lignes physiques correspondantes.

Conséquence : la quasi-totalité des xmlids standards `uom.product_uom_*` pointaient vers la **mauvaise ligne** en base. Exemples concrets trouvés sur `coheliance18` avant correction :

| xmlid | pointait vers | contenu réel de cette ligne |
|---|---|---|
| `uom.product_uom_hour` | id 4 | **"g" (grammes)** |
| `uom.product_uom_day` | id 3 | **"kg"** |
| `uom.product_uom_kgm` | id 12 | **"m³"** |
| `uom.product_uom_meter` | id 5 | **"Jours"** |
| `uom.product_uom_qt` | id 23 | *(n'existe pas)* → crash |

Seuls `product_uom_unit`, `product_uom_dozen` et les catégories `Unité`, `Poids`, `Temps de travail`, `Longueur/distance` étaient corrects.

Ce problème est indépendant du module `uom_unece` : c'est un défaut latent de la migration 14 → 18, présent sur toutes les bases migrées de cette façon. Le module `uom_unece` n'a fait que le révéler, en étant le premier à référencer un xmlid `uom.*` invalide.

**Important** : ceci n'affecte aucune donnée métier existante (articles, lignes de commande...). Ces enregistrements référencent une unité par son `id` concret en base, jamais par xmlid. Seule la résolution de `env.ref('uom.xxx')` (par du code standard ou custom, à la création de nouveaux enregistrements) était impactée.

## Solution appliquée

Plutôt que de modifier le module OCA `uom_unece` (non souhaité, pour rester proche de l'upstream), le correctif a été ajouté dans le module maison `is_coheliance18`, sous forme de script de migration Odoo classique :

```
is_coheliance18/migrations/18.0.1.0.1/post-migrate.py
```

(version du module montée de `18.0.1.0.0` à `18.0.1.0.1` dans `__manifest__.py` pour déclencher son exécution).

Le script :

1. Recorrige le `res_id` des xmlids `uom.category`/`uom.uom` qui pointaient vers la mauvaise ligne existante (ex: `product_uom_hour` → bonne ligne "Heures").
2. Crée les lignes physiquement absentes (catégorie `Surface`, unités `product_uom_millimeter`, `uom_square_meter`, `product_uom_yard`, `uom_square_foot`) et pointe leur xmlid dessus. Ces unités ne sont pas utilisées fonctionnellement mais doivent exister pour que `uom_unece/data/unece.xml` (non modifié) puisse résoudre toutes ses références.

Le script ne touche que la table `ir_model_data` — aucune donnée métier n'est modifiée.

Le même correctif doit être dupliqué dans le module équivalent de `is_coheliance_formation18`, la base `coheliance-formation18` présentant exactement la même corruption (vérifié ligne à ligne, identique à l'octet près).

## Pour aller plus loin

Si un article a été créé par le passé via du code qui résolvait un xmlid `uom.*` alors incorrect (ex: un service supposé en "Heures" mais créé avec l'unité "Grammes" à cause du bug), son `uom_id` reste figé sur la mauvaise unité même après ce correctif — celui-ci ne corrige que les résolutions futures, pas les données déjà créées. À auditer au cas par cas si une incohérence d'unité est suspectée sur un article existant.
