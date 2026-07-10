# Connexion à Super PDP

Super PDP utilise **OAuth 2.1** pour l'authentification. Source : https://www.superpdp.tech/documentation/4

---

## Option 1 — Client Credentials (recommandée pour un usage développeur/direct)

À utiliser si vous gérez un seul compte ou en mode bac à sable.

Paramètres à renseigner :
- **Token Endpoint** : `https://api.superpdp.tech/oauth2/token`
- **grant_type** : `client_credentials`
- **client_id** et **client_secret** : à récupérer dans votre interface Super PDP

---

## Option 2 — Authorization Code (pour délégation d'accès utilisateur)

À utiliser si vos utilisateurs connectent leur propre compte Super PDP via votre logiciel.

Paramètres à renseigner :
- **Authorization Endpoint** : `https://api.superpdp.tech/oauth2/authorize`
- **Token Endpoint** : `https://api.superpdp.tech/oauth2/token`
- **grant_type** : `authorization_code`
- **client_id** et **client_secret** : depuis l'interface Super PDP
- **Redirect URL** : doit correspondre exactement à celle configurée dans Super PDP
- **Scopes** : laisser vide

---

## Utilisation du token

Une fois le token obtenu, chaque requête API doit inclure l'en-tête HTTP :

```
Authorization: Bearer <access_token>
```

---

## Durée de vie des tokens

- **access_token** : 30 minutes (renouvelable automatiquement via une bibliothèque OAuth 2.1)
- **refresh_token** (Authorization Code uniquement) : 1 an glissant (réinitialisé à chaque utilisation)

> Il est fortement conseillé d'utiliser une bibliothèque OAuth 2.1 qui gère automatiquement
> le renouvellement de l'access_token et la rotation du refresh_token.

> **Note — module Akretion (`l10n_fr_einvoicing`)** : le renouvellement des tokens est
> **entièrement automatisé par le module**, sans intervention de l'utilisateur.
> - **Client Credentials** : avant chaque appel API, le module vérifie si l'`access_token` est
>   encore valide et en récupère un nouveau si nécessaire.
> - **Authorization Code** : la rotation du `refresh_token` est gérée automatiquement via
>   `pyfrctc.get_session()`.

---

## Créer une application dans Super PDP (obtenir client_id et client_secret)

1. Connectez-vous à l'interface Super PDP
2. Cliquez sur **Applications** dans le menu de gauche
3. Créez une nouvelle application
4. Pour le **Type d'application**, choisissez **Confidentielle (serveur Node, Python, PHP, etc.)**
   - Ce type est adapté à Odoo : le `client_id` et le `client_secret` sont stockés côté serveur
     et ne sont jamais exposés à l'utilisateur final
   - Choisir "Publique" serait réservé aux applications web front-end ou mobiles, où le secret
     ne peut pas être gardé confidentiel
5. **Option 1 — Client Credentials uniquement (mon choix)** : aucune Redirect URL à renseigner, passez à l'étape suivante
   **Option 2 — Authorization Code uniquement** : renseignez la **Redirect URL** (URL de callback de votre instance Odoo, ex : `https://votre-odoo.com/fr_ctc_onboarding_callback`). Elle doit être identique dans Super PDP et dans Odoo.
6. Copiez le **client_id** et le **client_secret** générés
7. Dans Odoo, renseignez ces valeurs sur la fiche société dans les paramètres de la plateforme accréditée
8. Le bouton "Test API" permet de vérifier que c'est OK

---

## Révocation d'un token

Endpoint de révocation (protocole RFC 7009) : `https://api.superpdp.tech/oauth2/revoke`

- Révoquer un **access_token** : supprime uniquement ce jeton
- Révoquer un **refresh_token** : supprime le refresh_token et tous les access_tokens associés
