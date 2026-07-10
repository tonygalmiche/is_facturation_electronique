# Module `base_view_inheritance_extension`

**Source :** OCA / server-tools  
**Version :** 18.0.1.0.2  
**Catégorie :** Technique (dépendance cachée)  
**Dépendances :** `base` uniquement

---

## Objectif

Étend le moteur d'héritage de vues d'Odoo en ajoutant de **nouvelles opérations XPath** sur les attributs des vues XML. Sans ce module, modifier un attribut existant (ex. `context`, `domain`, `class`) dans une vue héritée oblige à réécrire la valeur complète. Ce module permet des **modifications ciblées** sans écraser ce qui existe déjà.

Il est utilisé par `l10n_fr_siret` (et d'autres modules OCA) pour appliquer des héritages de vues complexes de façon propre.

---

## Nouveaux Menus

Aucun menu ajouté. Module purement technique.

---

## Nouveaux Champs

Aucun nouveau champ. Le module hérite du modèle `ir.ui.view` pour y ajouter trois nouvelles opérations.

---

## Nouvelles Opérations XPath

### 1. `operation="update"` — Fusion de dictionnaire

Fusionne un dictionnaire Python dans un attribut existant (principalement `context`), sans écraser les clés déjà présentes.

```xml
<field name="partner_id" position="attributes">
    <attribute name="context" operation="update">
        {"default_type": "out_invoice"}
    </attribute>
</field>
```

Utilise le parsing AST (sans `eval()`) pour une manipulation sécurisée.

---

### 2. `operation="text_add"` — Ajout de texte

Concatène du texte avant et/ou après la valeur existante d'un attribut. Utile pour ajouter des classes CSS ou des segments à un attribut de chaîne.

```xml
<field name="state" position="attributes">
    <attribute name="class" operation="text_add">fw-bold {old_value}</attribute>
</field>
```

Le marqueur `{old_value}` est remplacé par la valeur actuelle de l'attribut.

---

### 3. `operation="domain_add"` — Fusion de domaine

Fusionne un domaine Odoo avec celui existant via un opérateur logique (`AND` par défaut, ou `OR`). Supporte une condition optionnelle.

```xml
<field name="partner_id" position="attributes">
    <attribute name="domain" operation="domain_add" join_operator="AND">
        [('is_company', '=', True)]
    </attribute>
</field>
```

Attributs disponibles :
- `join_operator` : `AND` (défaut) ou `OR`
- `condition` : expression booléenne — le domaine n'est ajouté que si la condition est vraie

---

## Résumé

| Opération | Cas d'usage typique |
|-----------|---------------------|
| `update` | Ajouter des clés à un `context` sans réécrire l'existant |
| `text_add` | Ajouter une classe CSS à `class`, concaténer des chaînes |
| `domain_add` | Restreindre un `domain` de recherche sans réécrire le filtre existant |
