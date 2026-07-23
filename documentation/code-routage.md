# Code de routage

Le **code de routage** (ou "adresse électronique") est l'identifiant qui
permet à une PA/PDP de savoir **à qui livrer techniquement une facture
électronique**, distinct du SIREN/SIRET qui identifie juridiquement
l'entreprise.

## Où il apparaît dans le XML Factur-X

Généré par `account_invoice_en16931`, injecté dans le XML via le champ
**BT-49** (adresse électronique de l'acheteur), sourcé sur
`fr_directory_line_id.identifier` — cf.
[account_invoice_en16931/models/account_move.py:340-341](../../account_invoice_en16931/models/account_move.py#L340-L341).
Pour le secteur public, il apparaît aussi via `BT-46 (0240)` / `BT-56-0` —
cf. [l10n_fr_account_invoice_en16931.md](l10n_fr_account_invoice_en16931.md).

## Le modèle `fr.directory.line`

Fourni par `l10n_fr_einvoicing` (annuaire national CTC), alimenté par le
bouton "Directory Sync". Chaque partenaire peut avoir plusieurs lignes,
typées via le champ `type`
([fr_directory_line.py:29-39](../../l10n_fr_einvoicing/models/fr_directory_line.py#L29-L39)) :

| Type | Description |
|---|---|
| `siren` | L'identifiant SIREN sert lui-même de code de routage |
| `siret` | SIRET |
| `routing_code` | Vrai code de routage Peppol (ex. `0225:315143296_268`) |
| `suffix` | Suffixe |
| `error` | Ligne malformée |

Sur une facture, `fr_directory_line_id` (et son `identifier` recopié dans
`fr_directory_line_identifier`) est choisi automatiquement à la confirmation
(`_compute_fr_directory_line_id`,
[l10n_fr_einvoicing/models/account_move.py:118-140](../../l10n_fr_einvoicing/models/account_move.py#L118-L140)) :

1. `partner_id.default_fr_directory_line_id` du contact facturé, sinon
2. `default_fr_directory_line_id` du partenaire commercial (société mère),
   sinon
3. la ligne active unique de l'annuaire pour ce partenaire s'il n'y en a
   qu'une.

## Exemple : client CLAIR SARL (SIREN 350759684)

Recherche faite sur base `facturation-electronique18`.

Ligne d'annuaire du partenaire (`res_partner.id = 16`) :

```sql
select id, type, identifier, siren, routing_code, state, partner_id
from fr_directory_line where siren='350759684';
```

```
 id | type  | identifier |   siren   | routing_code | state  | partner_id
----+-------+------------+-----------+--------------+--------+-----------
 43 | siren | 350759684  | 350759684 |              | active |        16
```

→ une seule ligne, de type `siren`, sans `routing_code` renseigné.

Facture envoyée à ce client :

```sql
select id, name, partner_id, fr_directory_line_id, fr_directory_line_identifier,
       state, move_type
from account_move where partner_id=16 order by id desc limit 1;
```

```
 id |      name      | partner_id | fr_directory_line_id | fr_directory_line_identifier | state  |  move_type
----+----------------+------------+-----------------------+-------------------------------+--------+-------------
 42 | FAC/2026/00012 |         16 |                    43 | 350759684                     | posted | out_invoice
```

→ la facture a utilisé la ligne 43, donc le code de routage effectivement
envoyé dans le XML (BT-49) pour CLAIR SARL est **le SIREN nu `350759684`**,
pas une adresse Peppol distincte.

## À ne pas confondre : la découverte réseau Peppol (SML)

Une recherche du même SIREN directement dans l'outil de Super PDP renvoie
un résultat différent, basé sur le protocole Peppol SML (Service Metadata
Locator) :

- **Domaine DNS (NAPTR)** :
  `MBHEPDHSSQB3AGWW6YNV2PSCADB46VRGDLDUUO62L3FQDSSKMWLQ.iso6523-actorid-upis.participant.sml.prod.tech.peppol.org`
  — une requête DNS NAPTR standard du réseau Peppol. Le préfixe est le hash
  (base32 de l'empreinte MD5) de l'identifiant participant complet
  (`0225:350759684`, schéma `iso6523-actorid-upis` pour le SIREN français
  sur Peppol).
- **Point d'accès** : `https://api.superpdp.tech/peppol/production` — Super
  PDP est déclaré comme la PDP/Access Point Peppol de ce SIREN en
  production.

Ce lookup confirme que ce SIREN est bien enregistré sur le réseau Peppol
avec un point d'accès réel, mais c'est une résolution DNS en direct sur le
réseau Peppol — **pas** ce qui est stocké dans `fr.directory.line` côté
annuaire national CTC, ni ce qu'Odoo a effectivement écrit dans le XML de
la facture envoyée. Pour CLAIR SARL, l'annuaire Odoo n'a qu'une ligne
`siren` (pas de ligne `routing_code`), donc c'est le SIREN qui a servi de
code de routage, indépendamment de ce que révèle la découverte Peppol.
