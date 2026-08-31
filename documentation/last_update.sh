#!/bin/bash
# Recherche la date de dernière mise à jour (dernier commit) sur GitHub pour
# chaque module/lib listé dans installation.md.
#
# Pour les modules qui vivent dans un monorepo (OCA/akretion), on interroge le
# dernier commit qui touche le sous-dossier du module (paramètre `path` de
# l'API GitHub), pas juste le dernier commit du dépôt entier.
#
# Usage : ./last_update.sh
# Optionnel : export GITHUB_TOKEN=... pour augmenter la limite de rate (60 ->
# 5000 requêtes/heure).

set -euo pipefail

AUTH_HEADER=()
if [ -n "${GITHUB_TOKEN:-}" ]; then
  AUTH_HEADER=(-H "Authorization: Bearer $GITHUB_TOKEN")
fi

# name|owner/repo|branch|path (path vide = dépôt entier, pas un module dans un monorepo)
ENTRIES=(
  "account_invoice_en16931|akretion/fr-einvoicing|16.0|account_invoice_en16931"
  "l10n_fr_account_invoice_en16931|akretion/fr-einvoicing|16.0|l10n_fr_account_invoice_en16931"
  "l10n_fr_siret|OCA/l10n-france|16.0|l10n_fr_siret"
  "account_tax_unece|akretion/community-data-files|16-backport-account_tax_unece-vatex|account_tax_unece"
  "uom_unece|OCA/community-data-files|16.0|uom_unece"
  "account_payment_unece|OCA/community-data-files|16.0|account_payment_unece"
  "base_unece|OCA/community-data-files|16.0|base_unece"
  "intrastat_base|OCA/intrastat-extrastat|16.0|intrastat_base"
  "base_view_inheritance_extension|OCA/server-tools|16.0|base_view_inheritance_extension"
  "account_payment_method_base|OCA/account-payment|16.0|account_payment_method_base"
  "l10n_fr_einvoicing|akretion/fr-einvoicing|16.0|l10n_fr_einvoicing"
  "l10n_fr_siret_account|OCA/l10n-france|18.0|l10n_fr_siret_account"
  "l10n_fr_einvoicing_import|akretion/fr-einvoicing|16.0|l10n_fr_einvoicing_import"
  "account_invoice_import|OCA/edi|16.0|account_invoice_import"
  "account_invoice_import_facturx|OCA/edi|16.0|account_invoice_import_facturx"
  "base_facturx|OCA/edi|16.0|base_facturx"
  "base_business_document_import|OCA/edi|16.0|base_business_document_import"
  "lib factur-x|akretion/factur-x||"
  "lib pyfrctc|akretion/pyfrctc||"
  "Saxon Server|willemvlh/saxon-server||"
)

# Récupère toutes les lignes (nom formaté, URL, date) avant l'affichage, pour
# pouvoir calculer la largeur de chaque colonne et aligner le tableau final.
COL1=("Module / Lib")
COL2=("Dépôt GitHub")
COL3=("Dernière mise à jour")

for entry in "${ENTRIES[@]}"; do
  IFS='|' read -r name repo branch path <<< "$entry"

  if [ -n "$path" ]; then
    url="https://api.github.com/repos/$repo/commits?path=$path&per_page=1"
    [ -n "$branch" ] && url="$url&sha=$branch"
  else
    url="https://api.github.com/repos/$repo/commits?per_page=1"
  fi

  response="$(curl -s "${AUTH_HEADER[@]}" "$url")"
  date="$(echo "$response" | grep -m1 '"date"' | sed -E 's/.*"date": *"([^"]+)".*/\1/')"

  if [ -z "$date" ]; then
    date="ERREUR (${response:0:80})"
  else
    date="$(date -d "$date" '+%Y-%m-%d' 2>/dev/null || echo "$date")"
  fi

  COL1+=("\`$name\`")
  COL2+=("https://github.com/$repo")
  COL3+=("$date")

  # évite de se faire rate-limiter (60 req/h anonyme)
  sleep 1
done

# Largeur de chaque colonne = plus longue valeur (en-tête compris)
w1=0; w2=0; w3=0
for v in "${COL1[@]}"; do (( ${#v} > w1 )) && w1=${#v}; done
for v in "${COL2[@]}"; do (( ${#v} > w2 )) && w2=${#v}; done
for v in "${COL3[@]}"; do (( ${#v} > w3 )) && w3=${#v}; done

sep1="$(printf -- '-%.0s' $(seq 1 "$w1"))"
sep2="$(printf -- '-%.0s' $(seq 1 "$w2"))"
sep3="$(printf -- '-%.0s' $(seq 1 "$w3"))"

printf '| %-*s | %-*s | %-*s |\n' "$w1" "${COL1[0]}" "$w2" "${COL2[0]}" "$w3" "${COL3[0]}"
printf '|-%s-|-%s-|-%s-|\n' "$sep1" "$sep2" "$sep3"
for i in "${!COL1[@]}"; do
  [ "$i" -eq 0 ] && continue
  printf '| %-*s | %-*s | %-*s |\n' "$w1" "${COL1[$i]}" "$w2" "${COL2[$i]}" "$w3" "${COL3[$i]}"
done
