#!/bin/bash
# Télécharge et met en place tous les modules OCA/Akretion nécessaires à la
# facturation électronique (cf. README.md pour l'arbre de dépendances complet).
#
# Ne gère PAS : les libs Python (factur-x, pyfrctc, cf. lib-factur-x.md /
# lib-pyfrctc.md) ni Saxon Server (cf. saxon-server.md) — installation séparée.
#
# Usage : ./installation-modules-oca.sh [dossier_destination]
# Par défaut, dossier_destination = /media/sf_dev_odoo/18.0/facturation-electronique

set -euo pipefail

DEST_DIR="${1:-/media/sf_dev_odoo/18.0/facturation-electronique}"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$DEST_DIR"

# repo|branche|module1,module2,...
REPOS=(
  "https://github.com/OCA/l10n-france.git|18.0|l10n_fr_siret,l10n_fr_siret_account"
  "https://github.com/OCA/server-tools.git|18.0|base_view_inheritance_extension"
  "https://github.com/akretion/fr-einvoicing.git|18.0|l10n_fr_einvoicing,l10n_fr_account_invoice_en16931,account_invoice_en16931"
  "https://github.com/OCA/community-data-files.git|18.0|base_unece,uom_unece,account_payment_unece"
  "https://github.com/OCA/account-payment.git|18.0|account_payment_method_base"
  "https://github.com/OCA/intrastat-extrastat.git|18.0|intrastat_base"
)

echo "== Modules OCA/Akretion standards =="
for entry in "${REPOS[@]}"; do
  IFS='|' read -r repo branch modules <<< "$entry"
  repo_name="$(basename "$repo" .git)"
  clone_dir="$TMP_DIR/$repo_name"

  echo "--- Clone $repo (branche $branch) ---"
  git clone -b "$branch" --depth 1 "$repo" "$clone_dir"

  IFS=',' read -ra module_list <<< "$modules"
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

# account_tax_unece : PR VATEX #277 non mergée, à récupérer depuis le fork
# Akretion tant que la PR n'est pas fusionnée dans OCA/community-data-files
# (cf. account_tax_unece.md)
echo "--- Clone account_tax_unece (fork Akretion, PR VATEX #277 non mergée) ---"
if [ -d "$DEST_DIR/account_tax_unece" ]; then
  echo "  [skip] account_tax_unece existe déjà dans $DEST_DIR, non écrasé"
else
  clone_dir="$TMP_DIR/community-data-files-vatex"
  git clone -b 18-account_tax_unece-vatex --depth 1 \
    https://github.com/akretion/community-data-files.git "$clone_dir"
  mv "$clone_dir/account_tax_unece" "$DEST_DIR/"
  rm -rf "$clone_dir"
  echo "  [ok] account_tax_unece -> $DEST_DIR/"
fi

echo
echo "== Terminé =="
echo "Modules installés dans : $DEST_DIR"
echo
echo "Étapes restantes (non gérées par ce script) :"
echo "  - lib Python factur-x >= 6.1 (cf. lib-factur-x.md)"
echo "  - lib Python pyfrctc >= 0.13 (cf. lib-pyfrctc.md)"
echo "  - Saxon Server (cf. saxon-server.md)"
echo "  - Mettre à jour la liste des applications dans Odoo, puis installer is_facturation_electronique"
