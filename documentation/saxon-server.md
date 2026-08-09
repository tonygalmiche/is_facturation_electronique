Lien : https://github.com/willemvlh/saxon-server

# À quoi sert Saxon Server ?

Saxon Server est un petit webservice open source qui expose la librairie Java **Saxon** (moteur XSLT/XQuery de l'éditeur **Saxonica**, fondé par Michael Kay, l'un des principaux rédacteurs des specs W3C XSLT 2.0/3.0 — implémentation de référence de ces normes) via une API HTTP. On lui envoie un fichier XML et une feuille de style XSL, il renvoie le résultat de la transformation.

Saxon existe en plusieurs éditions :

- **Saxon-HE** (Home Edition) — gratuite et open source, supporte déjà XSLT 2.0/3.0 + Schematron. C'est celle utilisée ici, par `saxonche` comme par Saxon Server.
- **Saxon-PE/EE** (Professional/Enterprise) — payantes, fonctionnalités avancées non nécessaires pour ce cas d'usage.

Dans le cadre de la réforme de la facturation électronique, ce serveur est utilisé pour la **validation Schematron** des fichiers Factur-X / UBL générés par Odoo :

- Les schématrons Factur-X (et ceux de la réforme française) utilisent des instructions **XSLT2**, hors la librairie Python `lxml` ne supporte que XSLT1. Saxonica est la seule implémentation complète de la norme Schematron qui supporte XSLT2.
- Historiquement, la lib `factur-x` (et `pyfrctc`) s'appuyait sur les bindings Python `saxonche` (qui utilisent GraalVM en interne pour exécuter le moteur Java depuis Python). Ce mécanisme provoquait un bug bloquant (crash fatal GraalVM) lorsqu'il était appelé depuis un thread/process qui n'avait pas initialisé le runtime Saxon — typiquement un cron ou un worker Odoo. Voir le détail du bug ici : https://github.com/akretion/pyfrctc/issues/3
- Pour contourner ce problème, la lib `factur-x` ne dépend plus de `saxonche` : elle envoie désormais une requête HTTP `POST /transform` (fichier XML + schematron XSL) à un serveur Saxon Server externe, qui répond au format SVRL (Schematron Validation Report Language).

En résumé : Saxon Server est un composant **externe et obligatoire** (au même titre qu'une base de données) pour pouvoir valider la conformité Schematron des factures Factur-X/UBL générées par Odoo Community, avant leur dépôt sur un PDP/Chorus Pro.

## Un seul serveur, appelé par deux libs différentes

`factur-x` ([lib-factur-x.md](./lib-factur-x.md)) et `pyfrctc` ([lib-pyfrctc.md](./lib-pyfrctc.md)) ont toutes les deux abandonné `saxonche` pour le même bug GraalVM et appellent donc toutes les deux Saxon Server en HTTP — mais elles ne valident pas le même document, et pas au même moment du cycle de vie d'une facture :

- **`factur-x`** valide la **facture elle-même** (XML Factur-X/UBL) contre le schématron Factur-X + celui de la réforme française, à la génération/validation de la facture (~2 appels par facture).
- **`pyfrctc`** valide les fichiers **CDAR** (*Cross Domain Acknowledgement and Response*), des documents de statut de cycle de vie distincts de la facture (approuvée, rejetée, en litige, payée... statuts AFNOR 200-220, cf. [l10n_fr_einvoicing.md](./l10n_fr_einvoicing.md)) — un CDAR est généré à **chaque événement de cycle de vie**, pas seulement à la création de la facture.

Les deux libs sont deux clients Python différents qui appellent le **même** service HTTP partagé (`http://localhost:5000/transform`), pour deux types de documents différents. 

## Existe-t-il une alternative plus simple à Saxon Server ?

Pas vraiment : Saxon (Home Edition, gratuit) est en pratique la **seule** implémentation libre complète de XSLT2/3 + Schematron — `lxml`/libxml2 ne supportent que XSLT1, insuffisant pour ces schématrons. `saxonche` (bindings Python du même moteur Saxon, en local sans serveur) serait plus simple côté architecture, mais c'est justement ce qui a été abandonné à cause du bug GraalVM en contexte cron/worker (cf. plus haut). Saxon Server n'est donc pas un choix parmi d'autres outils concurrents, mais un contournement de ce bug, avec le même moteur derrière. Le seul vrai levier de simplification serait d'isoler l'exécution de `saxonche` (ex. subprocess dédié par validation) pour éviter le bug sans passer par un serveur HTTP séparé — non testé ni recommandé ici, ce n'est pas l'approche retenue par les auteurs des libs.

## Point d'attention : le fichier CodeDB

Les schématrons Factur-X (profil EXTENDED) référencent un fichier externe `FACTUR-X_EXTENDED_codedb.xml` (via le fichier `Factur-X_1.09_EXTENDED.xsl`). Or Saxon Server ne permet pas d'envoyer ce fichier annexe à la volée dans la requête `/transform`. Trois solutions (cf. https://github.com/willemvlh/saxon-server/issues/23) :

- **Odoo sert lui-même le fichier CodeDB en HTTP** (comportement par défaut depuis `factur-x>=6.4` / module `account_invoice_en16931`, commit [`03a3f0f`](https://github.com/akretion/fr-einvoicing/commit/03a3f0fcb139805d90ca43e2298a7419446223ba) du 2026-07-14) : Odoo expose un controller public `GET /en16931/FACTUR-X_EXTENDED_codedb.xml` (fichier `controllers/get_facturx_codedb.py`, servi depuis la lib `factur-x` via `facturx_schematron_get_codedb_xml_file`) et transmet cette URL au serveur Saxon via le paramètre `saxon_server_codedb_base_url` (calculé par défaut à partir de `web.base.url` + `en16931/`, sans configuration nécessaire). Saxon Server n'a donc plus besoin d'accès Internet public ni d'accès filesystem local pour le CodeDB — juste d'un accès réseau vers Odoo. **C'est la solution par défaut désormais, plus besoin des deux options ci-dessous dans la majorité des cas.**
- **URL publique GitHub** (ancien comportement par défaut de la lib factur-x, avant `factur-x>=6.4`) : le XSL pointe vers l'URL GitHub du fichier CodeDB. Ajoute de la latence et nécessite un accès Internet depuis le serveur Saxon. À éviter en prod — remplacé par la solution ci-dessus sur les versions récentes.
- **Accès filesystem local** (toujours possible, prioritaire si configuré) : lancer Saxon Server avec l'option `--insecure` (ou `-i`) qui autorise l'accès au système de fichiers, et mettre à disposition un répertoire contenant le(s) fichier(s) `FACTUR-X_<profil>_codedb.xml` (seul le profil `EXTENDED` est utilisé par l'implémentation Odoo, donc seul `FACTUR-X_EXTENDED_codedb.xml` est nécessaire — disponible ici : https://github.com/akretion/factur-x/tree/master/src/facturx/xsd_and_schematron/facturx-extended). Le chemin de ce répertoire se configure côté Odoo via le `ir.config_parameter` `en16931.saxon_server_codedb_dir` — **non exposé dans l'UI de configuration de la compta depuis le commit ci-dessus** (retiré de `wizards/res_config_settings.py`/`.xml`), à renseigner directement dans Réglages > Technique > Paramètres Système si on veut forcer cette option plutôt que le partage HTTP par défaut. Si ce paramètre est renseigné, il prend le pas sur `saxon_server_codedb_base_url` (cf. `account_move.py`, `search_read_facturx_xml`).
**Note** : on a testé une variante avec le CodeDB servi via une URL nginx locale au lieu d'un chemin filesystem — sans intérêt avec l'option filesystem, `--insecure` reste nécessaire dans ce cas (le mode sécurisé par défaut de Saxon Server bloque aussi l'accès réseau via `document()`, pas seulement l'accès au filesystem). Voir la note plus bas dans la section CodeDB pour le détail. Avec la solution HTTP par défaut (Odoo sert le fichier), `--insecure` reste également nécessaire car Saxon Server doit pouvoir faire un `document()` réseau vers l'URL Odoo.

# Installation

## JAR Java

Prérequis : `openjdk-<version>-jre` installé (Java 17+ recommandé, cf. release notes du projet).

```bash
apt install openjdk-17-jre

mkdir -p /opt/saxon-server
cd /opt/saxon-server
wget https://github.com/willemvlh/saxon-server/releases/download/v1.15/saxon-server-1.15.jar


# Utilisateur système dédié (pas de shell, pas de home réel)
adduser --system --group --no-create-home saxon-server

# Le répertoire d'installation doit lui appartenir
chown -R saxon-server:saxon-server /opt/saxon-server

java -jar saxon-server-1.15.jar --insecure
```

Liste des versions disponibles (pour récupérer une version plus récente le cas échéant) : https://github.com/willemvlh/saxon-server/releases

`/opt/saxon-server` est l'emplacement recommandé sur Debian pour un logiciel tiers installé manuellement (hors gestion de paquets `apt`).

Options utiles au lancement :

| Option | Rôle |
| --- | --- |
| `-p, --port` | Port d'écoute (défaut : 5000) |
| `-i, --insecure` | Autorise l'accès filesystem, les appels de fonctions externes, l'accès aux propriétés système (nécessaire pour le CodeDB en local) |
| `-t, --timeout` | Timeout d'une transformation en ms (défaut : 2 min) |
| `-c, --config` | Fichier de configuration Saxon |
| `-d, --debug` | Active les logs de debug |

## Faire tourner Saxon Server en service (systemd)


Créer le fichier `/etc/systemd/system/saxon-server.service` :

```ini
[Unit]
Description=Saxon Server (XSLT/XQuery HTTP transformation)
After=network.target

[Service]
Type=simple
User=saxon-server
Group=saxon-server
WorkingDirectory=/opt/saxon-server
ExecStart=/usr/bin/java -jar /opt/saxon-server/saxon-server-1.15.jar --insecure
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Adapter `ExecStart` selon les options souhaitées (port, timeout, etc., cf. tableau ci-dessus). Si l'accès au répertoire CodeDB en local est utilisé (option `--insecure`), s'assurer que l'utilisateur `saxon-server` a bien les droits de lecture sur ce répertoire.

Activer et démarrer le service :

```bash
systemctl daemon-reload
systemctl enable --now saxon-server
```

Vérifier l'état et les logs :

```bash
systemctl status saxon-server
journalctl -u saxon-server -f
```

## Sécurité : ne jamais exposer le port sur Internet

Saxon Server ne propose **aucune option pour restreindre son adresse d'écoute** (pas de `--host`/`--bind` : il écoute sur `0.0.0.0`, donc sur toutes les interfaces, y compris l'IP publique si le serveur en a une — confirmé en ligne de commande sur `ss -tlnp` et dans la doc officielle du projet). Le README du projet le confirme lui-même dans sa section "Security" :

> *"Note that this alone is not enough to protect against attackers. It is recommended to place a reverse proxy server in front of this application to take care of IP whitelisting, rate limiting, etc."*

Avec l'option `--insecure`, le serveur autorise en plus l'accès au système de fichiers et des fonctions XSLT comme `document()`, qui permettent de lire des fichiers arbitraires sur le serveur (ex : `/etc/passwd`, clés SSH) si quelqu'un peut envoyer une requête `/transform` avec un XSL malveillant. Le port doit donc être bloqué en entrée pour tout le monde sauf `localhost` (et éventuellement le serveur Odoo si celui-ci tourne sur une autre machine) via un pare-feu, puisque l'application elle-même ne le permet pas.

`fail2ban` seul ne suffit pas : il ne fait que bannir des IP après des tentatives suspectes, il ne restreint pas l'exposition du port. Il faut un pare-feu. Sur Debian, le plus simple pour démarrer est `ufw` :

**Attention** : la politique par défaut d'`ufw` est *"deny incoming"* — dès l'activation, **tout** le trafic entrant est bloqué sauf ce qui est explicitement autorisé. Si Odoo (via nginx) tourne sur le même serveur, il faut donc autoriser SSH **et** les ports web (nginx) avant d'activer `ufw`, sinon on coupe aussi l'accès à Odoo, pas seulement à Saxon Server.

```bash
apt install ufw

# Autoriser SSH avant d'activer le pare-feu, sinon risque de coupure d'accès
ufw allow OpenSSH

# Autoriser les ports web utilisés par nginx pour Odoo (sinon Odoo devient
# injoignable dès l'activation d'ufw)
ufw allow 80/tcp
ufw allow 443/tcp
# ou, si le profil nginx est enregistré (ufw app list) :
# ufw allow 'Nginx Full'

# Ne rien ouvrir pour le port 5000 : par défaut ufw bloque tout le trafic entrant
# qui n'a pas de règle "allow" explicite, donc le port 5000 reste fermé en externe
ufw enable
ufw status verbose
```

Comme le port Saxon (5000) n'a aucune règle `allow`, il reste inaccessible depuis l'extérieur alors que `curl http://127.0.0.1:5000/...` en local continue de fonctionner (le trafic loopback n'est pas concerné par les règles de pare-feu).

Si le serveur Odoo est sur une autre machine, ouvrir le port uniquement pour son IP :

```bash
ufw allow from <IP_du_serveur_Odoo> to any port 5000 proto tcp
```

Vérifier régulièrement que le port n'est pas joignable depuis l'extérieur, par exemple depuis une autre machine ou un scanner en ligne (ex : `nmap <IP_publique> -p 5000` depuis une machine externe au réseau).

Pour tester rapidement sans dépendre de `curl`/`nmap`, on peut utiliser `/dev/tcp` de bash, qui échoue immédiatement (timeout) si le port est bloqué :

```bash
# Depuis une machine EXTERNE à la VM (doit échouer / timeout)
timeout 3 bash -c "echo > /dev/tcp/<IP_de_la_VM>/5000" \
  && echo "PORT 5000 OUVERT (problème !)" \
  || echo "PORT 5000 BLOQUE (attendu)"

# Depuis la VM elle-même, en loopback (doit réussir, Odoo doit continuer à fonctionner)
timeout 3 bash -c "echo > /dev/tcp/127.0.0.1/5000" \
  && echo "local OK" || echo "local FAIL"
```

### Voir la configuration ufw

```bash
ufw status verbose      # état (actif/inactif), politique par défaut, règles actives avec ports/IP
ufw status numbered     # même chose mais avec un numéro devant chaque règle (utile pour ufw delete <n>)
ufw app list            # liste des profils d'applications enregistrés (ex: Nginx Full, OpenSSH)
cat /etc/ufw/user.rules # fichier brut des règles IPv4 persistées
```

`ufw disable` : désactive le pare-feu (tout redevient joignable), mais les règles restent enregistrées dans `/etc/ufw/user.rules` — un `ufw enable` suffit à tout réactiver, pas besoin de les ressaisir. `systemctl stop ufw` n'a pas le même effet : le service s'arrête mais les règles déjà chargées dans le noyau ne sont pas retirées.

# Tester le serveur (avant de configurer Odoo)

## Test rapide avec les fichiers d'exemple du dépôt saxon-server

Le dépôt GitHub du projet fournit ses propres fichiers de test (utilisés pour ses tests unitaires), pratiques pour un premier test sans avoir besoin d'un vrai Factur-X : https://github.com/willemvlh/saxon-server/tree/master/src/test/resources/tv/mediagenix/xslt/transformer

```bash
wget https://raw.githubusercontent.com/willemvlh/saxon-server/master/src/test/resources/tv/mediagenix/xslt/transformer/xml/dummy.xml
wget https://raw.githubusercontent.com/willemvlh/saxon-server/master/src/test/resources/tv/mediagenix/xslt/transformer/xsl/test-1.xsl

curl http://localhost:5000/transform -F xml=@dummy.xml -F xsl=@test-1.xsl
# Réponse attendue : hello
```

La requête est en `multipart/form-data` avec les paramètres `xml` et `xsl` (le paramètre `xml` est optionnel si le XSL ne fait pas de `transform` sur un document, par exemple pour générer un document depuis le XSL seul).

## Test réaliste : validation Schematron Factur-X

Pour tester ce qui sera réellement utilisé par Odoo, envoyer une facture XML Factur-X (ou UBL) avec le schématron Factur-X en `xsl` : le serveur doit répondre avec un rapport au format SVRL (XML).

Le dépôt `akretion/factur-x` fournit des factures XML d'exemple (fixtures de test), dont une au profil EXTENDED (celui utilisé par Odoo) : https://github.com/akretion/factur-x/tree/master/tests/fixtures/xml

```bash
wget https://raw.githubusercontent.com/akretion/factur-x/master/tests/fixtures/xml/factur-x-extended.xml
wget https://raw.githubusercontent.com/akretion/factur-x/master/src/facturx/xsd_and_schematron/facturx-extended/Factur-X_1.09_EXTENDED.xsl

# Retirer le BOM UTF-8 en tête du fichier XML (sinon la détection auto XML/JSON
# de Saxon Server échoue, cf. piège 1 ci-dessous)
sed -i '1s/^\xef\xbb\xbf//' factur-x-extended.xml

curl http://localhost:5000/transform -F xml=@factur-x-extended.xml -F xsl=@Factur-X_1.09_EXTENDED.xsl
```

Le schématron `Factur-X_1.09_EXTENDED.xsl` et le fichier CodeDB associé sont disponibles ici : https://github.com/akretion/factur-x/tree/master/src/facturx/xsd_and_schematron/facturx-extended (voir le point d'attention sur le CodeDB plus haut).

### Deux pièges rencontrés lors du premier test

1. **BOM UTF-8 dans le fichier XML** : la fixture `factur-x-extended.xml` téléchargée commence par un caractère BOM invisible avant `<?xml ...?>`, ce qui casse la détection automatique XML/JSON de Saxon Server (erreur `Invalid JSON input ... Unexpected character '<'`). Le `sed` déjà inclus dans le bloc ci-dessus le retire avant l'envoi.

2. **Fichier CodeDB manquant sur le serveur** (si on utilise `--insecure` + accès filesystem local, cf. plus haut) : le schématron référence `FACTUR-X_EXTENDED_codedb.xml` via un chemin **relatif**, que Saxon résout par rapport au **répertoire de travail du process Saxon Server** (`WorkingDirectory` du service systemd, ici `/opt/saxon-server`) — pas par rapport au dossier depuis lequel on envoie la requête `curl`. Sans ce fichier au bon endroit, l'erreur est : `I/O error reported by XML parser processing file:/opt/saxon-server/FACTUR-X_EXTENDED_codedb.xml`. Il faut donc le déposer directement dans le `WorkingDirectory` du service, avec les droits de l'utilisateur `saxon-server` :

```bash
cd /opt/saxon-server
wget https://raw.githubusercontent.com/akretion/factur-x/master/src/facturx/xsd_and_schematron/facturx-extended/FACTUR-X_EXTENDED_codedb.xml
chown saxon-server:saxon-server FACTUR-X_EXTENDED_codedb.xml
```

**nginx ne permet pas d'éviter `--insecure`** : testé en pratique sur `bookworm`, que le CodeDB soit servi en local (fichier) ou via une URL nginx locale, Saxon Server a besoin de `--insecure` dans les deux cas (le mode sécurisé par défaut bloque aussi l'accès réseau via `document()`, pas seulement l'accès au filesystem). Passer par nginx n'a donc pas d'intérêt ici.

## Configuration côté Odoo

Une fois le serveur testé et accessible, renseigner sur la page de configuration de la compta (exposé par le module [account_invoice_en16931](./account_invoice_en16931.md), `wizards/res_config_settings.py`) :

- `en16931.saxon_server_url` — l'URL du serveur Saxon (ex : `http://localhost:5000`).

Le CodeDB n'a normalement plus besoin de configuration manuelle (cf. section CodeDB plus haut) : Odoo le sert lui-même via HTTP, à partir de `web.base.url`. Deux `ir.config_parameter` restent disponibles pour forcer un autre comportement, mais **ne sont plus exposés dans l'UI** de cette page — à renseigner directement dans Réglages > Technique > Paramètres Système si besoin :

- `en16931.saxon_server_codedb_base_url` — pour forcer une autre URL de base que `web.base.url` (ex : si Saxon Server ne peut pas résoudre le nom d'hôte public d'Odoo et qu'il faut lui donner une URL interne) ;
- `en16931.saxon_server_codedb_dir` — pour revenir à l'ancien comportement (chemin local sur le serveur Saxon, `--insecure` obligatoire) ; si renseigné, il est prioritaire sur `saxon_server_codedb_base_url`.

## Incident rencontré (historique, versions < `factur-x` 6.4) : "Read timed out" sur le schématron `base`

**Note** : cet incident concernait le comportement par défaut *avant* le passage au partage HTTP du CodeDB par Odoo (cf. section CodeDB plus haut, `factur-x>=6.4`). Sur les versions actuelles, Odoo sert le CodeDB depuis lui-même par défaut (réseau local/interne), donc ce scénario (dépendance à une URL publique GitHub) ne devrait plus se reproduire sans intervention volontaire. Conservé ici à titre de contexte.

Erreur observée à la validation d'une facture :

```
Failed to validate the factur-x XML file against the Saxon schematron server.
Error: Check 'base' failed in the POST request to saxon server on
http://localhost:5000/transform: HTTPConnectionPool(host='localhost', port=5000):
Read timed out. (read timeout=5)
```

**Le serveur Saxon n'était pas en panne** (actif, répond en <50ms sur un test basique, et le schématron `fr-ctc` passait en 2,4s). Cause : `en16931.saxon_server_codedb_dir` n'était pas renseigné dans `ir_config_parameter` → la lib `factur-x` va chercher `FACTUR-X_EXTENDED_codedb.xml` via l'URL publique GitHub à chaque appel du schématron `base` (log `"Replacing codedb XML files by public URLs..."`), au lieu du fichier local déjà présent dans `/opt/saxon-server`. Ce chemin réseau, additionné à la recompilation du XSL (~2s), a dépassé le timeout **codé en dur à 5s** côté client Python (`facturx.py:167`, `SAXON_SERVER_TIMEOUT = 5`, non configurable) — probablement juste après un redémarrage du service (JVM "à froid").

**Action faite à l'époque** : Comptabilité > Configuration, bloc EN16931 :
- `Specific Saxon Server URL` → `http://localhost:5000` (si vide)
- `Saxon Server CodeDB dir` → `/opt/saxon-server` (champ depuis retiré de l'UI, cf. note ci-dessus — équivalent aujourd'hui : renseigner `en16931.saxon_server_codedb_dir` dans Réglages > Technique > Paramètres Système)

Ceci fait passer le CodeDB par le filesystem local (déjà en place, cf. section CodeDB plus haut) au lieu du réseau, ce qui élimine la dépendance à GitHub et la marge fragile par rapport au timeout de 5s. Sur les versions actuelles, le partage HTTP par défaut (Odoo sert le CodeDB) résout ce même problème sans configuration.

## Incident rencontré (2026-08-03) : "Read timed out" après redémarrage du service

Même symptôme que l'incident historique ci-dessus (`Check 'base' failed ... Read timed out (read timeout=5)`), mais cause différente : configuration correcte (factur-x 6.6, CodeDB servi en HTTP par Odoo, `web.base.url` en local répond en 44ms). Test réel du premier appel `/transform` juste après un redémarrage du service Saxon : **4,1s**, tout près du timeout de 5s codé en dur côté client. Les appels suivants (JVM chaude) : **2,0-2,4s**, largement sous la limite.

Cause : premier appel après redémarrage (JIT froid + compilation du XSL ~1,8 Mo) qui flirte avec le timeout non configurable. Pas de fix appliqué (config déjà correcte) — pistes possibles si ça se reproduit : patcher `SAXON_SERVER_TIMEOUT` dans la lib (écrasé aux upgrades), ping périodique pour garder la JVM chaude, ou remonter le problème en amont sur `akretion/factur-x`.

## Test depuis Odoo

1. Aller sur la page de configuration de la compta et cliquer sur **"Check config for EN16931 invoicing"** : ce bouton vérifie que la configuration (taxes, précisions décimales, codes d'exonération, etc.) est correcte pour générer des factures conformes EN16931. Cette étape ne teste pas directement Saxon Server, mais est un prérequis.
2. Faire une **requête d'annuaire** (Directory sync) sur un client de test et sur la société elle-même (ne pas oublier de sélectionner la ligne d'annuaire), afin que les deux entités disposent d'une ligne d'annuaire valide.
3. Valider une facture client de test : la génération du fichier Factur-X déclenche automatiquement l'appel au serveur Saxon pour la validation Schematron (schématron Factur-X **et** schématron de la réforme française). Si la connexion au serveur échoue ou si la validation Schematron échoue, Odoo doit remonter une erreur explicite.
4. En cas d'échec, vérifier :
   - que le serveur Saxon est bien démarré et joignable depuis Odoo (`curl http://<host>:5000/transform ...`) ;
   - que l'option `--insecure` est bien active (nécessaire dans tous les cas dès qu'un CodeDB est utilisé, local ou via URL), et que le chemin/URL configuré côté Odoo est bien accessible **depuis le process du serveur Saxon** (pas forcément le même serveur qu'Odoo) ;
   - les logs du serveur Saxon (option `-d/--debug` pour plus de détails).

# Point de vigilance : performance / validation en masse

Chaque appel `/transform` recompile le schématron (~1,8 Mo de XSL) à chaque requête, Saxon Server ne mettant pas en cache les stylesheets compilés entre appels HTTP — observé en pratique : **~2s par schématron**. Odoo appelle **2 schématrons par facture** (Factur-X de base + réforme française "fr-ctc"), soit **~4-5s de latence par validation de facture**. Correct pour une validation unitaire, mais problématique en validation en masse (plusieurs factures d'un coup), qui deviendrait très lente si elle est faite de façon synchrone et séquentielle. Vérifier si le module Odoo (`l10n_fr_einvoicing`/`account_invoice_en16931`) traite ces validations en tâche de fond (ex. via `queue_job` OCA) avant de déployer sur un volume de factures important.

# Références

- Dépôt du projet : https://github.com/willemvlh/saxon-server
- Releases (jar) : https://github.com/willemvlh/saxon-server/releases
- Bug GraalVM ayant motivé l'abandon de `saxonche` : https://github.com/akretion/pyfrctc/issues/3
- Problème du fichier CodeDB externe : https://github.com/willemvlh/saxon-server/issues/23
- Fichier CodeDB Factur-X EXTENDED : https://github.com/akretion/factur-x/tree/master/src/facturx/xsd_and_schematron/facturx-extended
- Contexte complet (discussion Alexis de Lattre) : voir [akretion.md](./akretion.md)
