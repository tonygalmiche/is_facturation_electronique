#!/bin/bash
# Télécharge et met en place les modules OCA/Akretion nécessaires à la
# facturation électronique, selon le cas d'installation souhaité
# (cf. installation.md pour le détail des modules et de leur rôle).
#
# Ne gère PAS : les libs Python (factur-x, pyfrctc, cf. lib-factur-x.md /
# lib-pyfrctc.md) ni Saxon Server (cf. saxon-server.md) — installation séparée.
#
# Usage : ./installation-modules-oca.sh <cas> [dossier_destination]
#   cas = 1 : génération d'une facture Factur-X/EN16931, sans envoi sur la PA
#   cas = 2 : cas 1 + envoi de la facture sur la PA
#   cas = 3 : cas 2 + réception des factures fournisseurs depuis la PA
# Par défaut, dossier_destination = /media/sf_dev_odoo/16.0/facturation-electronique

set -euo pipefail

usage() {
  echo "Usage : $0 <cas:1|2|3> [dossier_destination]" >&2
  echo "  1 : génération Factur-X/EN16931, sans envoi sur la PA" >&2
  echo "  2 : cas 1 + envoi de la facture sur la PA" >&2
  echo "  3 : cas 2 + réception des factures fournisseurs depuis la PA" >&2
  exit 1
}

CAS="${1:-}"
case "$CAS" in
  1|2|3) ;;
  *) usage ;;
esac

DEST_DIR="${2:-/media/sf_dev_odoo/16.0/facturation-electronique}"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$DEST_DIR"

# module -> repo|branche (account_tax_unece est géré à part, cf. plus bas)
#
# NB (dépendances spécifiques à la branche 16.0, différentes de la 18.0,
# vérifiées sur les __manifest__.py réels de chaque module) :
#   - account_payment_method_base n'existe pas en 16.0 (apparu en 18.0) ;
#     account_payment_unece dépend en 16.0 de account_payment_mode
#     (OCA/bank-payment) à la place.
#   - account_invoice_en16931 dépend en plus, en 16.0 uniquement, de
#     account_payment_partner (OCA/bank-payment).
#   - base_business_document_import dépend en plus, en 16.0 uniquement, de
#     pdf_helper (OCA/edi).
#   - l10n_fr_siret_account n'existe pas en branche 16.0 chez OCA/l10n-france
#     (module apparu à partir de la 18.0), mais n'est en réalité pas une
#     dépendance requise par l10n_fr_einvoicing (cf. documentation/backport-16.0.md)
#     : le cas 2 reste donc installable sans lui.
declare -A MODULE_REPO=(
  [account_invoice_en16931]="https://github.com/akretion/fr-einvoicing.git|16.0"
  [l10n_fr_account_invoice_en16931]="https://github.com/akretion/fr-einvoicing.git|16.0"
  [l10n_fr_siret]="https://github.com/OCA/l10n-france.git|16.0"
  [uom_unece]="https://github.com/OCA/community-data-files.git|16.0"
  [account_payment_unece]="https://github.com/OCA/community-data-files.git|16.0"
  [base_unece]="https://github.com/OCA/community-data-files.git|16.0"
  [intrastat_base]="https://github.com/OCA/intrastat-extrastat.git|16.0"
  [base_view_inheritance_extension]="https://github.com/OCA/server-tools.git|16.0"
  [account_payment_mode]="https://github.com/OCA/bank-payment.git|16.0"
  [account_payment_partner]="https://github.com/OCA/bank-payment.git|16.0"
  [l10n_fr_einvoicing]="https://github.com/akretion/fr-einvoicing.git|16.0"
  [l10n_fr_einvoicing_import]="https://github.com/akretion/fr-einvoicing.git|16.0"
  [account_invoice_import]="https://github.com/OCA/edi.git|16.0"
  [account_invoice_import_facturx]="https://github.com/OCA/edi.git|16.0"
  [base_facturx]="https://github.com/OCA/edi.git|16.0"
  [base_business_document_import]="https://github.com/OCA/edi.git|16.0"
  [pdf_helper]="https://github.com/OCA/edi.git|16.0"
)

# Modules propres à chaque cas (cf. installation.md)
CASE1_MODULES=(account_invoice_en16931 l10n_fr_account_invoice_en16931 l10n_fr_siret uom_unece account_payment_unece base_unece intrastat_base base_view_inheritance_extension account_payment_mode account_payment_partner)
CASE2_MODULES=(l10n_fr_einvoicing)
CASE3_MODULES=(l10n_fr_einvoicing_import account_invoice_import account_invoice_import_facturx base_facturx base_business_document_import pdf_helper)

MODULES=("${CASE1_MODULES[@]}")
[ "$CAS" -ge 2 ] && MODULES+=("${CASE2_MODULES[@]}")
[ "$CAS" -ge 3 ] && MODULES+=("${CASE3_MODULES[@]}")

echo "== Cas d'installation $CAS : ${#MODULES[@]} module(s) OCA/Akretion à installer =="

# Regroupe les modules par dépôt pour ne cloner chaque dépôt qu'une fois
declare -A REPO_MODULES=()
for module in "${MODULES[@]}"; do
  repo_branch="${MODULE_REPO[$module]}"
  REPO_MODULES["$repo_branch"]+="$module,"
done

for repo_branch in "${!REPO_MODULES[@]}"; do
  IFS='|' read -r repo branch <<< "$repo_branch"
  repo_name="$(basename "$repo" .git)"
  clone_dir="$TMP_DIR/$repo_name"

  echo "--- Clone $repo (branche $branch) ---"
  git clone -b "$branch" --depth 1 "$repo" "$clone_dir"

  IFS=',' read -ra module_list <<< "${REPO_MODULES[$repo_branch]}"
  for module in "${module_list[@]}"; do
    if [ -d "$DEST_DIR/$module" ]; then
      echo "  [skip] $module existe déjà dans $DEST_DIR, non écrasé"
      continue
    fi
    if [ ! -d "$clone_dir/$module" ]; then
      echo "  [ERREUR] $module introuvable dans $repo_name" >&2
      continue
    fi
    mv "$clone_dir/$module" "$DEST_DIR/"
    echo "  [ok] $module -> $DEST_DIR/"
  done

  rm -rf "$clone_dir"
done

# account_tax_unece (requis dès le cas 1) : PR VATEX #277 non mergée, à
# récupérer depuis le fork Akretion tant qu'elle n'est pas fusionnée dans
# OCA/community-data-files (cf. account_tax_unece.md)
echo "--- Clone account_tax_unece (fork Akretion, PR VATEX #277 non mergée) ---"
if [ -d "$DEST_DIR/account_tax_unece" ]; then
  echo "  [skip] account_tax_unece existe déjà dans $DEST_DIR, non écrasé"
else
  clone_dir="$TMP_DIR/community-data-files-vatex"
  git clone -b 16-backport-account_tax_unece-vatex --depth 1 \
    https://github.com/akretion/community-data-files.git "$clone_dir"
  mv "$clone_dir/account_tax_unece" "$DEST_DIR/"
  rm -rf "$clone_dir"
  echo "  [ok] account_tax_unece -> $DEST_DIR/"
fi

echo
echo "== Terminé =="
echo "Modules installés dans : $DEST_DIR (cas $CAS)"
echo
echo "Étapes restantes (non gérées par ce script) :"
echo "  - lib Python factur-x >= 6.3 (cf. lib-factur-x.md)"
if [ "$CAS" -ge 2 ]; then
  echo "  - lib Python pyfrctc >= 0.12 (cf. lib-pyfrctc.md)"
fi
echo "  - Saxon Server (cf. saxon-server.md)"
echo "  - Mettre à jour la liste des applications dans Odoo, puis installer les modules"
