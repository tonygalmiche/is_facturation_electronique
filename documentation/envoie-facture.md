## Erreur "Aucune ligne d'annuaire pour la société n'a été sélectionnée sur la facture"

### Symptôme
Lors de la validation d'une facture client (`account.move`), Odoo refuse avec :
> Aucune ligne d'annuaire pour la société n'a été sélectionnée sur la facture '...'.

### Cause
Le champ `company_fr_directory_line_id` (module `l10n_fr_einvoicing`, [account_move.py](../../l10n_fr_einvoicing/models/account_move.py)) est un champ calculé et stocké :

```python
@api.depends("company_id")
def _compute_company_fr_directory_line_id(self):
```

Il ne dépend que de `company_id`, pas de `partner_id.default_fr_directory_line_id`. Si la ligne d'annuaire (`fr.directory.line`) de la société a été créée/mise à jour **après** la création de la facture, le champ reste vide en base (`NULL`) car rien ne déclenche son recalcul.

Exemple constaté :
- Facture créée à 05:48:45
- Ligne d'annuaire de la société (SIREN) créée à 05:50:49, donc après la facture
- Résultat : `company_fr_directory_line_id` reste vide sur la facture, alors que la ligne d'annuaire existe bel et bien sur la société

### Diagnostic en base (psql, base `facturation-electronique18`)
```bash
psql -d facturation-electronique18 -c "select id,fr_directory_line_id,company_fr_directory_line_id from account_move where id=<ID_FACTURE>"
```

Vérifier aussi la ligne d'annuaire de la société (partner_id = société) :
```bash
psql -d facturation-electronique18 -c "select id,partner_id,identifier,state,active from fr_directory_line where partner_id=<ID_PARTNER_SOCIETE>"
```

### Solution (sans shell / sans SQL)
Le champ `company_fr_directory_line_id` est déclaré `readonly=False` malgré le `compute`, donc éditable manuellement dans l'UI :

1. Ouvrir la facture concernée (brouillon)
2. Aller dans l'onglet **« Facturation électronique »**
3. Renseigner manuellement le champ **« Company Directory Line »** avec la ligne d'annuaire de la société
4. Enregistrer, puis revalider la facture

## Erreur "Tax '20% S' has no UNECE Tax Type" (blocage EN16931)

### Cause
Sur la taxe concernée (ex: `20% S`), les champs **« Type de taxe de l'UNECE »** (`unece_type_id`) et/ou **« Catégorie de taxe de l'UNECE »** (`unece_categ_id`) ne sont pas renseignés.

### Valeurs à renseigner pour une TVA standard (20%, vente de service en France)
- **Type de taxe de l'UNECE** : `VAT` (`[VAT] Value added tax`)
- **Catégorie de taxe de l'UNECE** : `S` (`[S] Standard rate`)

### Piège : recherche sensible à la casse
En tapant `vat` (minuscules) dans le champ, **aucun résultat n'apparaît**, alors que la donnée existe bien en base (`unece_code_list`, type=`tax_type`, code=`VAT`).

**À retenir : toujours taper les codes UNECE en majuscules** (`VAT`, `S`, etc.), ou taper un extrait du nom complet (ex: "value added").

## Serveur Saxon (validation Schematron EN16931/CTC)

### Configuration
Le champ **« Specific Saxon Server URL »** (Configuration > eInvoicing, module `account_invoice_en16931`, paramètre système `en16931.saxon_server_url`) permet de spécifier une URL de serveur Saxon custom.

### Comportement si le champ est laissé vide
**Le serveur Saxon est quand même utilisé** — ce n'est pas une fonctionnalité désactivée par défaut. Si le paramètre est vide, la lib `factur-x` (utilisée par le module) retombe sur une URL par défaut codée en dur :
```python
# facturx/facturx.py
SAXON_SERVER_DEFAULT_URL = "http://localhost:5000/transform"
...
url = saxon_server_url
if url is None:
    url = SAXON_SERVER_DEFAULT_URL
```
Donc si un serveur Saxon écoute réellement sur `localhost:5000` sur la machine où tourne Odoo (ex: process Java lancé indépendamment, service système, container), il sera utilisé pour la validation Schematron même sans rien configurer côté Odoo.

### Vérifier si un serveur Saxon tourne en local
```bash
ss -tlnp | grep 5000
curl -s -o /dev/null -w '%{http_code}\n' --max-time 3 http://localhost:5000/transform
```
Un `404` sur un `GET` est normal (l'endpoint attend un `POST`) — ça confirme juste que le serveur répond.

### À retenir
- Ne pas confondre le serveur Saxon avec la plateforme d'envoi (`fr_ctc_accredited_platform`, ex: Super PDP) — ce sont deux choses indépendantes
- Champ vide ≠ fonctionnalité désactivée : vérifier si un serveur écoute sur `localhost:5000` avant de conclure que Saxon n'a pas été sollicité
- Par défaut, si l'appel au serveur Saxon échoue (pas de connexion), l'erreur est juste loguée (`raise_if_http_error=False`), la génération de la facture n'est pas bloquée

### Si le serveur Saxon est arrêté/injoignable : la facture part quand même, sans contrôle
Dans `facturx.py` (`xml_check_schematron`), en cas d'échec de la requête HTTP vers le serveur Saxon :
```python
except Exception as err:
    ...
    logger.warning(error_msg)
    if raise_if_http_error:
        raise RuntimeError(error_msg) from err
    logger.warning(f"Skipping schematron check '{check_type}'")
    continue
```
`raise_if_http_error` vaut `False` par défaut, et **n'est exposé nulle part** dans la chaîne d'appel utilisée par Odoo (`generate_xml()` / `generate_cii_xml()` ne le prennent même pas en paramètre). Résultat :
- Pas d'erreur bloquante dans Odoo
- Le contrôle Schematron (conformité EN16931/CTC) est silencieusement sauté
- La facture continue son cycle normal et part quand même (seul le contrôle XSD reste garanti, lui toujours exécuté en local)

**Il n'existe donc actuellement aucune option pour forcer/obliger cette validation.**

### Comment vérifier que la facture a bien été validée par Saxon
Rien n'est stocké en base sur le résultat du contrôle Schematron : il faut consulter les **logs serveur Odoo** au moment de la génération de la facture.
- Succès : `Sending HTTP POST request on http://localhost:5000/transform...` puis `Saxon server answered successfully for check '...'`
- Échec silencieux : `Check '...' failed in the POST request to saxon server...` puis `Skipping schematron check '...'`

Sur l'environnement de test, Odoo tourne sans `logfile` configuré (logs dans la console de la session, pas de fichier). Pour pouvoir grepper les logs a posteriori, ajouter dans le fichier de conf Odoo (ex: `/etc/odoo/facturation-electronique18.conf`) :
```ini
logfile = /var/log/odoo/odoo.log
```
puis relancer Odoo. Ensuite :
```bash
grep -i schematron /var/log/odoo/odoo.log
```

## Option ajoutée : "Obliger la validation Schematron Saxon"

Vu qu'il n'existait aucun moyen de forcer le blocage en cas d'échec/indisponibilité du serveur Saxon (voir section précédente), une option a été ajoutée **dans le module `is_facturation_electronique`** (sans toucher aux autres modules) :

- Champ `is_force_saxon_validation` sur `res.config.settings` (paramètre système `is_facturation_electronique.force_saxon_validation`)
- Visible dans **Comptabilité > Configuration > Paramètres**, section eInvoicing, sous les champs Saxon Server
- Fichiers : [models/res_config_settings.py](../models/res_config_settings.py), [models/account_move.py](../models/account_move.py), [views/res_config_settings_view.xml](../views/res_config_settings_view.xml)

Implémentation : `account.move.generate_facturx_xml()` est surchargé pour, si l'option est activée, rappeler `xml_check_schematron()` (lib `factur-x`) une seconde fois sur le XML déjà généré, avec `raise_if_http_error=True` cette fois. Si le serveur Saxon est injoignable ou si la validation échoue, une `UserError` bloque l'envoi de la facture.

**Contrepartie** : le contrôle Schematron est exécuté deux fois par facture quand l'option est active (une fois en silencieux dans `account_invoice_en16931`, une fois en mode strict dans `is_facturation_electronique`) — latence légèrement accrue, mais pas de duplication de code du module Akretion.

## Bug découvert grâce à cette option : montant de TVA toujours à 0.00 dans le XML EN16931

### Symptôme
Avec l'option "Obliger la validation" activée, **toutes les factures avec TVA** échouent le Schematron avec des erreurs du type `BR-FXEXT-S08b`, `BR-FXEXT-S-08ini`, `BR-FXEXT-S-08rev`, `BR-FXEXT-CO-15` : incohérence entre le montant de TVA déclaré et le montant réel de la facture.

### Cause (confirmée en générant et inspectant le XML brut)
Dans le bloc VAT breakdown (`BG-23` / `ApplicableTradeTax` au niveau du `ApplicableHeaderTradeSettlement`), le XML généré contient :
```xml
<ram:ApplicableTradeTax>
  <ram:CalculatedAmount>0.00</ram:CalculatedAmount>  <!-- devrait être le montant de TVA réel -->
  <ram:BasisAmount>0.00</ram:BasisAmount>            <!-- devrait être la base HT réelle -->
  ...
</ram:ApplicableTradeTax>
```
alors que le total de la facture (`SpecifiedTradeSettlementHeaderMonetarySummation`) est correct (`TaxBasisTotalAmount`, `GrandTotalAmount` bons).

Le code fautif, dans le module Akretion **`account_invoice_en16931`** ([models/account_move.py:394-411](../../account_invoice_en16931/models/account_move.py#L394-L411)) :
```python
for tax_dict, tax_vals in values_per_grouping_key.items():
    if tax_dict["unece_type_code"] == "VAT":
        bt110 += tax_vals.get("target_tax_amount_currency", 0)
        bt111 += tax_vals.get("target_tax_amount", 0)
        bg23.append({
            "BT-116": self.currency_id._en16931_format(
                tax_vals.get("target_base_amount_currency", 0)
            ),
            "BT-117": self.currency_id._en16931_format(
                tax_vals.get("target_tax_amount_currency", 0)
            ),
            ...
        })
```
Ce code lit des clés `target_base_amount_currency` / `target_tax_amount_currency` dans le dictionnaire retourné par `account.tax._aggregate_base_lines_aggregated_values()`. Or, dans le cœur Odoo 18 installé (`/opt/odoo18/addons/account/models/account_tax.py:2128` et suivants), cette méthode retourne des clés nommées **`base_amount_currency`** et **`tax_amount_currency`** (sans le préfixe `target_`). Les clés attendues par le module n'existent donc pas, `.get(clé, 0)` retombe systématiquement sur `0`, et le montant de TVA déclaré dans le XML est toujours nul, quelle que soit la facture.

C'est un problème de compatibilité entre le module Akretion `account_invoice_en16931` et l'API interne du cœur Odoo 18 installé (vraisemblablement un changement de nom de clé entre versions). **Toutes les factures avec TVA sont concernées**, pas seulement un cas isolé.

### Statut
Bug **côté module Akretion**, pas dans la config du client. Correction possible :
- soit corriger `account_invoice_en16931/models/account_move.py` pour utiliser les bons noms de clés (`base_amount_currency`, `tax_amount_currency`),
- soit surcharger `_prepare_bg23` dans `is_facturation_electronique` en attendant un correctif upstream,
- à remonter à Akretion/OCA si pas déjà corrigé dans une version plus récente du module.

## Vérification par rapport à l'annonce d'Alexis de Lattre (Akretion, voir [akretion.md](akretion.md))

### Ce qui est conforme
- lib `factur-x` version 6.1 ✅
- lib `pyfrctc` version 0.13 ✅
- PR OCA #277 (codes VATEX) intégrée : `VATEX-FR-FRANCHISE`, `VATEX-EU-O`, `VATEX-FR-CGI261C-*` présents dans les données ✅
- Chaîne de dépendances `l10n_fr_einvoicing` → `l10n_fr_account_invoice_en16931` → `account_invoice_en16931` ✅
- Ancien module OCA `account_invoice_facturx` bien absent/désinstallé ✅
- Saxon Server utilisé à la place de saxonche (confirmé par un process Java en écoute sur `localhost:5000`) ✅
- Bouton `Directory Sync` qui ne recalcule pas `company_fr_directory_line_id` sur l'historique des factures (comportement décrit par Alexis, cf section plus haut sur `company_fr_directory_line_id`) ✅

### Écart constaté : bouton "Check config for EN16931 invoicing"
Ce bouton, annoncé dans le mail comme présent sur la page de config de la compta, **n'existe ni en local ni sur la branche 18.0 distante** (`github.com/akretion/fr-einvoicing`, vérifié le 2026-07-13). `_en16931_checks()` existe bien dans le code (`account_invoice_en16931/models/res_company.py`) mais n'est appelée qu'automatiquement à la validation/génération de facture, jamais via un bouton dédié. Soit le bouton n'a en réalité jamais été implémenté, soit il a été retiré depuis.

### Écart plus important : le module local `account_invoice_en16931` est en retard sur la branche 18.0 distante
Le numéro de version du manifest n'a pas été incrémenté des deux côtés (`18.0.1.0.0`), ce qui masque le décalage, mais le contenu diffère :

| Élément | Local | Distant (18.0, vérifié 2026-07-13) |
|---|---|---|
| Champ `en16931_default_pdf_invoice` (choix Factur-X / Factur-X+UBL / PDF+UBL / PDF simple) sur `res.company` | absent | présent |
| Wizard `account.invoice.en16931.generate` (génération/téléchargement manuel en masse Factur-X/UBL/CII, formats zip/tar) | absent | présent (`wizards/account_invoice_en16931_generate.py` + vue) |
| Bug clés `target_base_amount_currency` / `target_tax_amount_currency` (TVA à 0 dans le XML, cf section précédente) | présent | **toujours présent aussi en distant**, pas encore corrigé par Akretion |

### Commandes pour mettre à jour le module `account_invoice_en16931` (et les autres modules Akretion/OCA du même dépôt)

Les modules ont été installés en clonant les dépôts puis en copiant seulement les sous-dossiers de modules (pas de `.git` conservé dans `/home/tony/Documents/Développement/dev_odoo/18.0/facturation-electronique/`). Pour mettre à jour :

```bash
# 1. Cloner (ou re-cloner) le dépôt à jour dans un répertoire de travail temporaire
cd /tmp
git clone --branch 18.0 --single-branch https://github.com/akretion/fr-einvoicing.git

# 2. Comparer avant d'écraser (recommandé) : voir ce qui a changé pour chaque module concerné
diff -rq /tmp/fr-einvoicing/account_invoice_en16931 \
  "/home/tony/Documents/Développement/dev_odoo/18.0/facturation-electronique/account_invoice_en16931"

# 3. Remplacer le module par la version à jour (adapter la liste selon les modules à mettre à jour :
#    l10n_fr_einvoicing, account_invoice_en16931, l10n_fr_account_invoice_en16931, etc.)
rsync -av --delete \
  --exclude '__pycache__' \
  /tmp/fr-einvoicing/account_invoice_en16931/ \
  "/home/tony/Documents/Développement/dev_odoo/18.0/facturation-electronique/account_invoice_en16931/"

# 4. account_tax_unece vient d'un dépôt différent (OCA/community-data-files) et la PR #277
#    (codes VATEX) n'est PAS mergée dans la branche par défaut à ce jour (vérifié 2026-07-13,
#    PR toujours "open"). Il faut donc récupérer la branche de la PR, pas la branche par défaut.
#    NB : au 2026-07-13, la PR n'a qu'un seul commit (2026-07-05), déjà intégré localement
#    (fichiers à jour au 2026-07-10) : pas besoin de la refaire tant qu'aucun nouveau commit
#    n'est ajouté à la PR. Vérifier avant de la re-cloner :
#    curl -s "https://api.github.com/repos/OCA/community-data-files/pulls/277/commits"
git clone https://github.com/OCA/community-data-files.git /tmp/community-data-files
cd /tmp/community-data-files && git fetch origin pull/277/head:pr-277 && git checkout pr-277

# 5. Mettre à jour le module dans Odoo (sur la VM, utilisateur odoo)
cd /opt/odoo18
python3 odoo-bin -c /etc/odoo/facturation-electronique18.conf -d facturation-electronique18 \
  -u account_invoice_en16931,l10n_fr_account_invoice_en16931,l10n_fr_einvoicing --stop-after-init
```

**Attention** : bien re-tester le contrôle Schematron après mise à jour, car le bug de TVA à 0 (`target_base_amount_currency`/`target_tax_amount_currency`) est toujours présent dans la version distante à ce jour — la mise à jour ne le corrigera pas à elle seule.

### Retour d'expérience : mise à jour réalisée le 2026-07-13

Modules mis à jour depuis `/tmp/fr-einvoicing` (branche 18.0, commit `49e17e8` du 2026-07-13) : `account_invoice_en16931`, `l10n_fr_account_invoice_en16931`, `l10n_fr_einvoicing`.

Deux blocages rencontrés pendant l'upgrade, résolus dans l'ordre :

1. **`External dependency version mismatch: factur-x>=6.3 (installed: 6.1)`**
   La nouvelle version du module exige `factur-x>=6.3`. Mettre à jour la lib avant de relancer l'upgrade :
   ```bash
   pip install --user --break-system-packages --upgrade git+https://github.com/akretion/factur-x
   ```
   Vérifier la version installée avec `pip show factur-x` (`facturx.VERSION` n'existe pas en tant qu'attribut, ne pas utiliser `python3 -c "import facturx; print(facturx.VERSION)"`).

2. **`AccountMove._prepare_en16931_dict() got an unexpected keyword argument 'pdf_invoice_bin'`**
   Cause : mise à jour partielle. `account_invoice_en16931` avait été synchronisé seul, alors que la nouvelle version ajoute un paramètre `pdf_invoice_bin` à `_prepare_en16931_dict()` (pour le support BG-24, PDF encapsulé dans le XML). Le module `l10n_fr_account_invoice_en16931`, qui surcharge cette méthode, n'avait pas été mis à jour en même temps et gardait l'ancienne signature sans ce paramètre.
   **Leçon : ne jamais mettre à jour `account_invoice_en16931` seul — toujours synchroniser en même temps tous les modules qui surchargent ses méthodes (`l10n_fr_account_invoice_en16931`, `l10n_fr_einvoicing`), au même commit du dépôt.**

3. **`ModuleNotFoundError: No module named 'openupgradelib'`**
   La nouvelle version de `l10n_fr_einvoicing` embarque un script de migration (`migrations/18.0.1.2.0/post-migration.py`, met à jour `fr_einvoicing_flow.odoo_invoice_format`) qui dépend de la lib `openupgradelib`, absente de l'environnement. Installer :
   ```bash
   pip install --user --break-system-packages openupgradelib
   ```

Après ces 3 correctifs, l'upgrade des 63 modules (dont `is_facturation_electronique`) s'est terminée sans erreur.

### Conséquence sur l'option "Obliger la validation Schematron Saxon" : méthode renommée

La mise à jour du 2026-07-13 a renommé la méthode surchargée par `is_facturation_electronique` :
- Avant : `generate_facturx_xml(self)` (un seul flavor Factur-X)
- Après : `generate_en16931_xml(self, flavor2level, pdf_invoice_bin=False)` (plusieurs flavors possibles : Factur-X, UBL, CII, en une seule fois, dict `{flavor: level}` → dict `{flavor: xml_bytes}`)

L'ancienne méthode `generate_facturx_xml` n'existe plus du tout dans `account_invoice_en16931`. L'override dans `is_facturation_electronique/models/account_move.py` a donc été mis à jour pour cibler `generate_en16931_xml` et boucler sur tous les flavors générés (pas seulement Factur-X).

**Point de vigilance pour l'avenir** : ce genre de renommage de méthode publique casse silencieusement les surcharges dans `is_facturation_electronique` sans erreur au chargement du module — l'erreur n'apparaît qu'à l'usage (génération réelle d'une facture). Après toute mise à jour d'`account_invoice_en16931`, il faut donc re-tester la génération d'une facture avec l'option "Obliger la validation" activée pour s'assurer que l'override fonctionne toujours.

### Confirmation : les erreurs Schematron réelles (pas juste l'indisponibilité de Saxon) ont toujours bloqué

En creusant le code de la lib `factur-x` (`xml_check_schematron`), il s'avère que **le paramètre `raise_if_http_error` ne concerne que les problèmes de communication** avec le serveur Saxon (serveur injoignable, timeout, HTTP≠200). Si le serveur répond correctement et détecte que le XML est réellement invalide (ce qui est le cas ici à cause du bug `target_base_amount_currency`), une exception est **systématiquement levée**, qu'importe la config :
```python
if errors:
    ...
    raise Exception(full_error)
```
Donc le bug de TVA à 0 documenté plus haut a **toujours bloqué la génération** dès que Saxon était joignable et répondait — l'option "Obliger la validation" ajoutée dans `is_facturation_electronique` ne sert donc que pour le cas plus étroit où le serveur Saxon est injoignable (silencieusement ignoré par défaut sans cette option).

