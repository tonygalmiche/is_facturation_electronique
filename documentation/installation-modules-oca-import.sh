#!/bin/bash
# Télécharge et met en place les modules OCA/Akretion nécessaires à l'import
# des factures fournisseur reçues de Super PDP (cf. import-depuis-super-pdp.md
# pour le détail de la chaîne de dépendances et des incidents rencontrés).
#
# Ne gère PAS : les libs Python (factur-x, pyfrctc) ni Saxon Server —
# déjà installées si vous avez suivi installation-modules-oca.sh au préalable.
#
# Usage : ./installation-modules-oca-import.sh [dossier_destination]
# Par défaut, dossier_destination = /media/sf_dev_odoo/18.0/facturation-electronique

set -euo pipefail

DEST_DIR="${1:-/media/sf_dev_odoo/18.0/facturation-electronique}"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$DEST_DIR"

# repo|branche|module1,module2,...
REPOS=(
  "https://github.com/OCA/edi.git|18.0|base_business_document_import,account_invoice_import,base_facturx,account_invoice_import_facturx"
  "https://github.com/akretion/fr-einvoicing.git|18.0|l10n_fr_einvoicing_import"
)

echo "== Modules OCA/Akretion pour l'import des factures fournisseur Super PDP =="
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

echo
echo "== Terminé =="
echo "Modules installés dans : $DEST_DIR"
echo
echo "Étapes restantes (non gérées par ce script) :"
echo "  - Mettre à jour la liste des applications dans Odoo, puis mettre à jour is_facturation_electronique"
echo "  - Voir import-depuis-super-pdp.md pour les incidents connus (matching SIREN, bug UnboundLocalError upstream)"
