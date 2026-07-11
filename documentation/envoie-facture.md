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

