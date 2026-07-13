## Test bac à sable Super PDP (Burger Queen / Tricatel)

Objectif : 2 sociétés Odoo correspondant aux 2 entreprises fictives du bac à sable, pour envoyer une facture de vente depuis l'une et la recevoir en facture d'achat dans l'autre via Peppol/Super PDP.

### 1. Créer les 2 sociétés
Réglages > Sociétés : créer "Burger Queen" et "Tricatel".

**Important** : utiliser le **"Numéro d'entreprise"** affiché sur Super PDP (`000000002` pour Burger Queen, `000000001` pour Tricatel) comme SIREN dans Odoo — **pas** le numéro visible dans le champ "Adresse" de la ligne d'annuaire (ex: `0225:315143296_268`, qui est l'adresse de routage Peppol, un identifiant différent). Erreur si on se trompe, à l'envoi de la facture :
> POST request on .../afnor-flow/v1/flows failed (400). L'entreprise (000000002) liée à cette session ne correspond pas au vendeur de la facture (315143296).
Super PDP vérifie que le vendeur déclaré dans la facture correspond à l'entreprise liée à la session API, via le numéro d'entreprise — pas l'adresse Peppol.

**Piège** : SIREN fictif → erreur "checksum is wrong" (contrainte Luhn dans `l10n_fr_siret`). On ne peut pas changer le numéro (il doit matcher l'annuaire Peppol du bac à sable). Contournement en base : voir [bac-a-sable-super-pdp.sql](bac-a-sable-super-pdp.sql) (section 1).

`res.company.siren` étant un champ related **stocké** (`related="partner_id.siren", store=True`, `l10n_fr_siret/models/res_company.py`), sur une table distincte de `res_partner`, un UPDATE SQL sur `res_partner` seul ne suffit pas : le script met aussi à jour `res_company`.

### 2. Config "France eInvoicing" (par société)
Compta > Paramètres, bloc France eInvoicing :
- Plateforme = SUPER PDP
- Identifiants API du bac à sable (`fr_ctc_client_id`/`secret`, ou bouton Onboarding si OAuth)
- Boutons "Test API" et "Check config for EN16931 invoicing"

### 3. Ligne d'annuaire des sociétés : ne pas utiliser "Directory Sync", l'insérer directement

Le bouton "Directory Sync" appelle l'API du bac à sable, mais la lib externe `pyfrctc` revalide elle-même la clé de Luhn du SIREN avant d'envoyer la requête (`get_directory_lines()`, `pyfrctc.py:452-453`) → erreur "SIREN ... is not valid.", même après avoir contourné la contrainte Odoo. Comme les SIREN du bac à sable sont fictifs, cette validation échoue toujours. On connaît déjà la ligne d'annuaire via l'interface Super PDP (Annuaire=Peppol, Adresse=`0225:<SIREN>_<suffixe>`), on l'insère donc directement en base, sans appeler l'API.

**Correctif complémentaire nécessaire** : la même clé de Luhn est revérifiée par `_get_siren()` ([l10n_fr_siret/models/res_partner.py:196-209](../../l10n_fr_siret/models/res_partner.py#L196-L209)), utilisée non seulement par "Directory Sync" mais aussi par la **validation de facture** (`_fr_ctc_is_vat_registered(raise_if_misconfigured=True)`, appelée depuis `account.move._post()`) → erreur "Le SIREN n'est pas défini" même si le champ est bien rempli en base. Correctif : surcharge de `_get_siren()` dans [is_facturation_electronique/models/res_partner.py](../models/res_partner.py) (accepte le SIREN stocké tel quel si la validation normale ne trouve rien). Ne pas remplacer le SIREN par un vrai numéro pour contourner ça : ça décorrélerait l'identité "assujetti TVA" de celle utilisée pour le routage Peppol (la ligne d'annuaire doit rester sur le SIREN fictif du bac à sable).

Script complet (SIREN, TVA, ligne d'annuaire, statut/nom de l'entité dans l'annuaire — ces 2 derniers n'étant sinon renseignés que par l'appel API réel) : [bac-a-sable-super-pdp.sql](bac-a-sable-super-pdp.sql). Le champ TVA est nécessaire pour la génération Factur-X (règle schematron BR-S-02 : identifiant TVA vendeur non vide) ; la clé est calculée par la formule standard FR à partir du SIREN.

La fonction SQL prend **3 identifiants distincts** en paramètre : `pg_temp.setup_sandbox_company(nom_société, numéro_entreprise, siren, adresse_peppol_complète)`. Le "Numéro d'entreprise" (SIREN/TVA du partenaire) et l'adresse de la ligne d'annuaire Peppol (routage) ne sont **pas** le même identifiant sur Super PDP (voir piège ci-dessus).

**Piège supplémentaire** : mettre l'adresse Peppol **complète avec suffixe** (`315143296_268` pour Burger Queen, `315143296_267` pour Tricatel), pas juste le SIREN nu. Sinon, comme les 2 sociétés du bac à sable partagent le même SIREN racine, le champ BT-49 envoyé dans le XML (adresse électronique acheteur, sourcé sur `fr_directory_line_id.identifier`, [account_move.py:340-341](../../account_invoice_en16931/models/account_move.py#L340-L341)) est identique pour les deux → Super PDP ne peut pas déterminer le vrai destinataire, et la facture n'apparaît jamais dans "Factures d'achat" côté acheteur (visible seulement côté "Factures de vente" de l'émetteur).

Pour ajouter une société, ajouter un appel `SELECT pg_temp.setup_sandbox_company(...)` en bas du fichier. Lancer avec :
```bash
psql -d facturation-electronique18 -f bac-a-sable-super-pdp.sql
```

### 4. Partenaires croisés
Dans Burger Queen : créer le client "Tricatel" (SIREN + Directory Sync). Symétrique dans Tricatel avec "Burger Queen" en fournisseur.

### 5. Envoyer
Facture client Burger Queen → Tricatel, valider, bouton "Send Immediately" (ou cron).

### 6. Recevoir
Côté Tricatel : lancer manuellement la tâche planifiée d'import des flux (Réglages > Actions planifiées) si besoin d'aller plus vite. Crée automatiquement une facture fournisseur brouillon.

### 7. Vérifier
Menu Facturation électronique : `direction=out, state=sent` côté Burger Queen ; `direction=in, state=done` + `move_id` côté Tricatel.
