## Modules installés dés le debut


facturation-electronique18=# select id,name,write_date,state from ir_module_module where state='installed' order by name;
 id  |        name        |         write_date         |   state   
-----+--------------------+----------------------------+-----------
  33 | auth_totp          | 2026-05-29 16:56:46.034282 | installed
  41 | base               | 2026-05-29 16:56:41.921737 | installed
  52 | base_import        | 2026-05-29 16:56:47.255581 | installed
  53 | base_import_module | 2026-05-29 16:56:47.574847 | installed
  63 | base_setup         | 2026-05-29 16:56:47.77111  | installed
  72 | bus                | 2026-05-29 16:56:48.345573 | installed
 144 | html_editor        | 2026-05-29 16:56:49.073065 | installed
 150 | iap                | 2026-05-29 16:56:49.666904 | installed
 640 | web                | 2026-05-29 16:56:45.555441 | installed
 641 | web_editor         | 2026-05-29 16:56:51.136345 | installed
 643 | web_tour           | 2026-05-29 16:56:48.937673 | installed
 644 | web_unsplash       | 2026-05-29 16:56:51.306014 | installed
(12 lignes)


## Modules installés pour avoir la facturation opérattionllen

doo@bookworm:/$ echo "select id,name,write_date,state from ir_module_module where state='installed' order by name" | psql facturation-electronique18
 id  |             name              |         write_date         |   state   
-----+-------------------------------+----------------------------+-----------
   1 | account                       | 2026-05-29 16:58:14.359453 | installed
   6 | account_edi_proxy_client      | 2026-05-29 16:58:15.353472 | installed
   7 | account_edi_ubl_cii           | 2026-05-29 16:58:16.026912 | installed
  10 | account_payment               | 2026-05-29 16:58:16.885165 | installed
  12 | account_peppol                | 2026-05-29 16:58:19.438938 | installed
  14 | account_qr_code_sepa          | 2026-05-29 16:58:19.700452 | installed
  19 | analytic                      | 2026-05-29 16:57:47.919528 | installed
  32 | auth_signup                   | 2026-05-29 16:57:48.313174 | installed
  33 | auth_totp                     | 2026-05-29 16:56:46.034282 | installed
  34 | auth_totp_mail                | 2026-05-29 16:57:48.513068 | installed
  36 | auth_totp_portal              | 2026-05-29 16:58:00.574047 | installed
  41 | base                          | 2026-05-29 16:57:27.709756 | installed
  51 | base_iban                     | 2026-05-29 16:58:17.131411 | installed
  52 | base_import                   | 2026-05-29 16:57:27.709756 | installed
  53 | base_import_module            | 2026-05-29 16:57:27.709756 | installed
  54 | base_install_request          | 2026-05-29 16:57:48.76505  | installed
  63 | base_setup                    | 2026-05-29 16:57:27.709756 | installed
  69 | base_vat                      | 2026-05-29 16:58:17.539354 | installed
  72 | bus                           | 2026-05-29 16:57:27.709756 | installed
  76 | certificate                   | 2026-05-29 16:57:32.212885 | installed
  96 | digest                        | 2026-05-29 16:58:01.131371 | installed
 113 | google_gmail                  | 2026-05-29 16:57:48.974163 | installed
 144 | html_editor                   | 2026-05-29 16:57:27.709756 | installed
 146 | http_routing                  | 2026-05-29 16:57:29.421172 | installed
 150 | iap                           | 2026-05-29 16:57:27.709756 | installed
 153 | iap_mail                      | 2026-05-29 16:57:49.122994 | installed
 155 | is_facturation_electronique   | 2026-05-29 16:58:17.688624 | installed
 222 | l10n_fr                       | 2026-05-29 16:57:28.786195 | installed
 223 | l10n_fr_account               | 2026-05-29 16:58:22.375724 | installed
 388 | mail                          | 2026-05-29 16:57:46.417007 | installed
 389 | mail_bot                      | 2026-05-29 16:57:49.329073 | installed
 428 | onboarding                    | 2026-05-29 16:57:30.57956  | installed
 430 | partner_autocomplete          | 2026-05-29 16:57:55.530376 | installed
 431 | payment                       | 2026-05-29 16:58:04.864669 | installed
 449 | phone_validation              | 2026-05-29 16:57:51.517742 | installed
 451 | portal                        | 2026-05-29 16:57:56.381472 | installed
 486 | privacy_lookup                | 2026-05-29 16:57:51.919615 | installed
 487 | product                       | 2026-05-29 16:57:54.956183 | installed
 522 | resource                      | 2026-05-29 16:57:31.800401 | installed
 523 | resource_mail                 | 2026-05-29 16:57:55.103488 | installed
 558 | sms                           | 2026-05-29 16:57:59.634375 | installed
 559 | snailmail                     | 2026-05-29 16:58:00.398828 | installed
 560 | snailmail_account             | 2026-05-29 16:58:18.118705 | installed
 562 | spreadsheet                   | 2026-05-29 16:58:05.198896 | installed
 563 | spreadsheet_account           | 2026-05-29 16:58:18.333656 | installed
 564 | spreadsheet_dashboard         | 2026-05-29 16:58:14.978009 | installed
 565 | spreadsheet_dashboard_account | 2026-05-29 16:58:18.550915 | installed
 637 | uom                           | 2026-05-29 16:57:29.260552 | installed
 640 | web                           | 2026-05-29 16:57:27.709756 | installed
 641 | web_editor                    | 2026-05-29 16:57:27.709756 | installed
 643 | web_tour                      | 2026-05-29 16:57:27.709756 | installed
 644 | web_unsplash                  | 2026-05-29 16:57:27.709756 | installed
(52 lignes)


# Module Akretion pour facturation electronique

l10n_fr_einvoicing
l10n_fr_siret
l10n_fr_siret_account
base_view_inheritance_extension


