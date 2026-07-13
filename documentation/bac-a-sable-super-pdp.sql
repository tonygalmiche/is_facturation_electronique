-- Bac à sable Super PDP : configuration SIREN + ligne d'annuaire pour les sociétés fictives
-- (Burger Queen, Tricatel, ...). Lancer avec :
--   psql -d facturation-electronique18 -f bac-a-sable-super-pdp.sql
--
-- Super PDP utilise 2 identifiants DIFFÉRENTS pour une même société fictive :
--   - "Numéro d'entreprise" (ex: 000000002 pour Burger Queen) : identité liée à la
--     session API. Doit être utilisé comme SIREN/TVA du partenaire dans Odoo, sinon
--     erreur à l'envoi : "L'entreprise (numéro d'entreprise) liée à cette session ne
--     correspond pas au vendeur de la facture (...)"
--   - Adresse de la ligne d'annuaire Peppol (ex: 0225:315143296_268) : uniquement pour
--     le routage. Reste tel quel dans fr_directory_line, ne pas le confondre avec le
--     numéro d'entreprise ci-dessus.
--
-- Important : mettre l'adresse COMPLÈTE avec suffixe (ex: "315143296_268"), pas juste
-- le SIREN nu. Sinon, si 2 sociétés du bac à sable partagent le même SIREN racine
-- (cas de Burger Queen/Tricatel, distingués par le suffixe _267/_268), le champ BT-49
-- envoyé dans le XML (account_move.py:340-341, sourcé sur fr_directory_line_id.identifier)
-- est identique pour les deux, Super PDP ne sait pas laquelle est le vrai destinataire,
-- et la facture n'arrive jamais en "Factures d'achat" côté acheteur.

CREATE OR REPLACE FUNCTION pg_temp.setup_sandbox_company(
    p_company_name text,
    p_numero_entreprise text,     -- SIREN/TVA du partenaire (identité/session API)
    p_siren_annuaire text,        -- SIREN "brut" de la société (colonne siren)
    p_directory_identifier text   -- adresse Peppol complète avec suffixe (colonne identifier)
)
RETURNS void AS $$
DECLARE
    v_partner_id integer;
    v_line_id integer;
BEGIN
    SELECT partner_id INTO v_partner_id FROM res_company WHERE name = p_company_name;
    IF v_partner_id IS NULL THEN
        RAISE EXCEPTION 'Aucune société trouvée avec le nom %', p_company_name;
    END IF;

    -- 1. SIREN sur le partenaire et sur res.company (contourne la contrainte de clé
    --    de Luhn : SIREN fictif du bac à sable). C'est le "Numéro d'entreprise",
    --    pas le SIREN de l'annuaire Peppol.
    UPDATE res_partner SET siren = p_numero_entreprise WHERE id = v_partner_id;
    UPDATE res_company SET siren = p_numero_entreprise WHERE name = p_company_name;

    -- 1b. TVA (nécessaire pour la règle schematron BR-S-02 : BT-31 Seller VAT
    --     Identifier non vide). Clé calculée par la formule standard FR
    --     ((12 + 3*(SIREN mod 97)) mod 97), même si le SIREN est fictif :
    --     le schematron ne vérifie que la présence de BT-31, pas sa validité.
    --     Contourne aussi la contrainte VAT d'Odoo (base_vat), qui réutilise la
    --     même validation Luhn du SIREN.
    UPDATE res_partner
    SET vat = 'FR' || lpad(
        ((12 + 3 * (p_numero_entreprise::bigint % 97)) % 97)::text, 2, '0'
    ) || p_numero_entreprise
    WHERE id = v_partner_id;

    -- 2. Ligne d'annuaire (contourne l'appel API bloqué par la même validation Luhn
    --    dans la lib pyfrctc) + mise en ligne par défaut sur le partenaire.
    --    identifier = adresse Peppol complète (avec suffixe) : c'est ce champ qui
    --    part dans le XML (BT-49) et sert au routage réel par Super PDP.
    INSERT INTO fr_directory_line
        (partner_id, identifier, type, siren, state, active, commitment_required)
    VALUES (
        v_partner_id, p_directory_identifier, 'siren', p_siren_annuaire,
        'active', true, false
    )
    ON CONFLICT (partner_id, identifier) DO UPDATE
        SET state = EXCLUDED.state, active = EXCLUDED.active
    RETURNING id INTO v_line_id;

    UPDATE res_partner SET default_fr_directory_line_id = v_line_id WHERE id = v_partner_id;

    -- 3. Statut de l'annuaire + nom de l'entité + date de synchro : ces champs ne sont
    --    remplis que par l'appel API réel (Directory Sync), qu'on ne peut pas utiliser
    --    ici (SIREN fictif). fr_directory_entity_type nécessite fr_directory_last_sync_date
    --    (contrainte res_partner.py:187-200), donc les 2 doivent être renseignés ensemble.
    UPDATE res_partner
    SET fr_directory_entity_type = 'private',
        fr_directory_name = p_company_name,
        fr_directory_last_sync_date = now()::date,
        fr_directory_closed = false
    WHERE id = v_partner_id;
END;
$$ LANGUAGE plpgsql;

-- Appeler la fonction pour chaque société fictive du bac à sable :
--                              (nom,           numéro entreprise, SIREN,       adresse Peppol complète)
SELECT pg_temp.setup_sandbox_company('Burger Queen', '000000002', '315143296', '315143296_268');
SELECT pg_temp.setup_sandbox_company('Tricatel',     '000000001', '315143296', '315143296_267');
