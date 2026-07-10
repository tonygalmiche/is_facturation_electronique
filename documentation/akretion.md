
Alexis de Lattre a commencé une discussion

Première release v18 "sérieuse"

J'ai publié aujourd'hui une première release "sérieuse" du code pour la réforme de la facturation électronique. Ce n'est pas encore une version finalisée, mais ça commence à être solide et prêt à entrer en phase finale de tests. Surtout, ça inclus la ré-écriture complète de la génération Factur-X (et UBL... même si il me reste encore un peu de travail sur UBL pour implémenter le modèle CreditNote en plus de Invoice... mais sinon tout est prêt, modulo l'ajout d'un paramètre de config pour choisir entre Factur-X et UBL... ça va arriver). La ré-écriture de la génération Factur-X était le dernier gros morceau qui manquait par rapport à l'architecture finale visée (je compte aussi ré-écriture l'import Factur-X et UBL, mais ça n'est pas critique, ça peut attendre car l'implémentation actuelle est saine).

Les composants de cette release:

    lib factur-x version 6.1

    lib pyfrctc version 0.13

    pour le module account_tax_unece, il faut prendre la PR OCA https://github.com/OCA/community-data-files/pull/277 qui ajoute les codes pour les motifs d'exonération (preneur d'une review sur cette PR)

    pour tous les autres modules : branche 18.0 de https://github.com/akretion/fr-einvoicing

Le module l10n_fr_einvoicing dépend maintenant du module l10n_fr_account_invoice_en16931 qui lui-même dépend du module account_invoice_en16931. Ces 2 derniers modules correspondent à ma ré-écriture de l'implémentation Factur-X (et UBL... c'est un module 2 en 1 vu que tout le code de génération XML, que ce soit pour UBL ou Factur-X est déporté dans la lib factur-X). Vous devrez donc au préalable désinstaller l'ancien module OCA account_invoice_facturx.

Autre changement très important : la lib factur-x ne dépend plus de la lib python saxonche pour la validation schematron. La validation schematron est une étape très importante pour s'assurer que le XML est valide et que le flux sera bien accepté par les PAs, sans rejet. Pour éviter le problème décrit dans ce bug report (https://github.com/akretion/pyfrctc/issues/3), après avoir étudié de nombreuses possibilités, j'ai finalement opté pour l'utilisation de Saxon Server, tel que disponible ici : https://github.com/willemvlh/saxon-server C'est un projet opensource qui a construit un petit webservice autour de la lib Java de Saxonica. Pour rappel, l'implémentation de Saxonica est la seulement implémentation complète de la norme schematron qui supporte les instructions XSLT2 (utilisée par les schématrons Factur-X et les schématrons de la réforme). Et l'implémentation première de Saxonica est en Java (saxonche était en fait un truc un peu tordu qui utilisait GraalVM pour compiler en quelque-sorte le code java original en python, ce qui n'est pas du tout anodin).

L'utilisation du serveur Saxon est très simple : on envoie une requête HTTP POST sur /transform avec le fichier XML Factur-X ou UBL à valider et le schematron au format XSL, et on obtient le résultat au format VRML XML. La solution semble parfaite... mais il y a un hic, que j'ai décrit ici : https://github.com/willemvlh/saxon-server/issues/23 Les schematrons de la norme Factur-X utilisent un fichier CODEDB XML externe (cf par exemple le fichier FACTUR-X_EXTENDED_codedb.xml (dispo ici https://github.com/akretion/factur-x/tree/master/src/facturx/xsd_and_schematron/facturx-extended) qui est appelé par le fichier schematron Factur-X_1.09_EXTENDED.xsl. Or le serveur saxon n'a pas prévu de pouvoir envoyer à la volée ce fichier "annexe". Il y a 2 moyens de contournement:

1) remplacer la référence au fichier FACTUR-X_EXTENDED_codedb.xml dans le fichier Factur-X_1.09_EXTENDED.xsl par une URL HTTP publique qui partage le fichier FACTUR-X_EXTENDED_codedb.xml publiquement. C'est ce que j'ai fait par défaut (je pointe vers l'URL github du fichier). Avantage : très simple. Inconvénient : ça ajoute de la latence et ça nécessite une connexion Internet. Bien en prototypage, mais pas conseillé en prod pour avoir de bonnes perfs.

2) lancer le serveur Saxon avec l'option "-i" ou "--insecure" (cf README du projet saxon server sur github) qui autorise le serveur Saxon à accéder au filesystem. Préparer un répertoire qui contient les fichiers CodeDB (l'implémentation Odoo n'utilise que le profil extended de Factur-X, donc vous n'avez normalement besoin que du fichier FACTUR-X_EXTENDED_codedb.xml) et passer le chemin de ce répertoire à la lib factur-x, ce qui se configure dans un ir.config_parameter sur Odoo. Pour faciliter les choses, j'ai fait en sorte que ce paramètre soit accessible sur la page de config de la compta :

Le projet Saxon Server fournit une image docker prête à l'emploi. Les 2 seules choses que vous avez à faire est d'ajouter l'option "insecure" et faire en sorte que l'image docker puisse accéder à un répertoire contenant le ou les fichiers FACTUR-X_<profil>_codedb.xml. Sinon, il suffit d'avoir le paquet openjdk-<version>-jre installé, de récupérer le fichier saxon-server-1.15.jar dans la dernière release du projet (https://github.com/willemvlh/saxon-server/releases) et de lancer la commande "java -jar saxon-server-1.15.jar --insecure"

J'aurai aimé que ce soit plus simple... mais j'ai exploré pas mal de pistes et c'est le plus simple que j'ai trouvé. Peut-être qu'un jour on pourra envoyer le fichier CODEDB dans la requête /transform et que ça permettra de simplifier un peu, mais on n'en est pas là.

Autre nouveauté : sur la page de config de la compta, il y a un nouveau bouton "Check config for EN16931 invoicing" : quand vous cliquez dessus, il vérifie tout un tas de paramètres sur la config des taxes à la vente, les précisions décimales, etc... pour vérifier que vous êtes prêt à utiliser le module account_invoice_en16931 ; les messages d'erreur qu'il affiche sont normalement assez explicites. Vous aurez par exemple besoin de mettre un code d'exonération sur les taxes TVA à la vente de catégorie E (ou d'archiver la taxe si vous ne l'utilisez pas, pour éviter ce message d'erreur bloquant)

Autre choses à savoir : si l'entité est non assujettie et que, par conséquent, il n'y a pas de taxes de TVA à la vente (ou qu'elles sont toutes archivées), il y a un paramètre en plus sur la page de config de la compta :

Vous devez par exemple sélectionner :

    VATEX-FR-FRANCHISE pour la société a un statut d'auto-entrepreneur qui est en dessous des seuls de TVA

    VATEX-EU-O (à vérifier) pour une association non assujetie à la TVA

Pour une société "normale" assujetie à la TVA, le nouveau module Factur-X impose à la validation des factures client une nouvelle règle, qui est directement issue de la norme EN16931 : il doit y avoir une et une seule taxe de type TVA par ligne de facture. Si la ligne de facture est exonérée de TVA pour une raison très spéciale (exemple : vente de timbre au tarif officiel La Poste), alors il faut mettre une taxe de type TVA à 0% avec catégorie UNECE = E (par exemple) avec le bon modif d'exonération configuré sur la taxe (en l’occurrence, pour cet exemple, il faut utiliser VATEX-FR-CGI261C-3).

Maintenant que cette première release "solide" est là, je vous propose de faire un maximum de tests dans les prochains jours et de remonter les bugs en public sur https://github.com/akretion/fr-einvoicing/issues

Pour les tests, il y a une chose particulièrement difficile à cibler en priorité : la génération Factur-X conforme au schematron. J'ai essayé de tester mon implémentation dans un maximum de scénarios : une ligne de facture avec prix négatif (qui créé une allowance avec chargeIndicator=False), des taxes DEEE/eco-participation, des factures en devise, des avoirs (même le scénario d'une ligne négative qui contient une eco-taxe fonctionne !), etc. mais il y a certainement encore des scénarios à tester/bugfixer.

Idée de test qui m'a été suggérée par l'un d'entre vous : sur une base de test d'un de vos clients, déployez le nouveau module de génération Factur-X, vérifiez la configuration des taxes, et générez les factures Factur-X avec la nouvelle implémentation en vous assurant que la conformité schématron est bien validée avec le serveur Saxon (mieux, vous pouvez faire une requête d'annuaire sur le client au préalable (et aussi sur la société, sans oublier de sélectionner la ligne d'annuaire), il testera les 2 niveaux de schématrons, le schematron Factur-X et celui de la réforme et pas seulement le schematron Factur-X). Attention : dans le XML de la facture, il y a non seulement la ligne d'annuaire du client mais aussi la ligne d'annuaire de votre société. Or, quand vous récupérez les lignes d'annuaire de votre société via un clic sur "Directory sync" sur la fiche partenaire, il ne va pas automatiquement invalider le champ compute "company_fr_directory_line_id" sur tout l'historique des factures client (d'ailleurs, ça serait surement un point d'amélioration : pouvoir le faire via un bouton ou un truc du genre).

P.S. pour ceux sont sur Odoo v18 et qui veulent déployer cette release en prod et qui ont des factures à déposer sur Chorus Pro, étant donné que SUPER PDP ne supporte pas encore l'envoi via Chorus Pro et que malheureusement Chorus Pro en mode portail ou API direct ne supporte que l'ancienne syntaxe XML de Factur-X et pas la nouvelle utilisée pour la réforme (oui, c'est n'importe quoi !!), j'ai fait une branche "18.0-tmp_hack_chorus" qui désactive la génération Factur-X sur les factures à destination d'un client Secteur public. Comme ça, on peut déposer la facture "PDF simple" sur le portail Chorus à la main... et passer dans l'OCR Chorus... à l'ancienne ! Mais au moins, ça permet de déposer la facture sur Chorus... sinon ça bloque !

Je pars 2 jours en vacances, jeudi 9 et vendredi 10 juillet. Je serai de retour le lundi 13 juillet... prêt à corriger tous les bugs que vous aurez trouvé. A vous de jouer pour les tests !

Alexis
Liens

    [18.0][IMP] account_tax_unece: add VAT exemption reason codes (VATEX) by alexis-via · Pull Request #277 · OCA/community-data-files

    Contribute to OCA/community-data-files development by creating an account on GitHub.
    GitHub - akretion/fr-einvoicing: Odoo modules for e-invoicing in France starting september 2026

    Odoo modules for e-invoicing in France starting september 2026 - akretion/fr-einvoicing
    _cdar_check_schematron crashes (GraalVM isolate) when called from a non-initializing thread / forked process (e.g. Odoo cron) · Issue #3 · akretion/pyfrctc

    Summary _cdar_check_schematron() aborts the whole process with a fatal GraalVM error when it is called from a thread/process that did not initialize the Saxon runtime — e.g. an Odoo cron/worker thr...
    GitHub - willemvlh/saxon-server: Easy XSLT &amp; XQuery transformation over HTTP

    Easy XSLT &amp; XQuery transformation over HTTP. Contribute to willemvlh/saxon-server development by creating an account on GitHub.
    XSL file that depend on an external XML file · Issue #23 · willemvlh/saxon-server

    I plan to use this great project saxon-server in the python factur-x lib to validate Factur-X XML files against the official schematrons, cf akretion/factur-x#81 But the official XSL file provided ...
    factur-x/src/facturx/xsd_and_schematron/facturx-extended/FACTUR-X_EXTENDED_codedb.xml at master · akretion/factur-x

    Python lib for Factur-X, the e-invoicing standard for France and Germany - akretion/factur-x
    factur-x/src/facturx/xsd_and_schematron/facturx-extended at master · akretion/factur-x

    Python lib for Factur-X, the e-invoicing standard for France and Germany - akretion/factur-x
    factur-x/src/facturx/xsd_and_schematron/facturx-extended/Factur-X_1.09_EXTENDED.xsl at master · akretion/factur-x

    Python lib for Factur-X, the e-invoicing standard for France and Germany - akretion/factur-x
    Releases · willemvlh/saxon-server

    Easy XSLT &amp; XQuery transformation over HTTP. Contribute to willemvlh/saxon-server development by creating an account on GitHub.
    Any plans for an Odoo 19.0 version? · Issue #7 · akretion/fr-einvoicing

    Hi, Thanks a lot for this project and for your work on the French e-invoicing reform for Odoo Community. I noticed the repository currently only has an 18.0 branch. Are there any plans to port thes...
    Issues · akretion/fr-einvoicing

    Odoo modules for e-invoicing in France starting september 2026 - Issues · akretion/fr-einvoicing

