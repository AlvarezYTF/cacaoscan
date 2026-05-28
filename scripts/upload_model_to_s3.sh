#!/usr/bin/env bash
# Sube un modelo entrenado al bucket de modelos con versionado en el path.
#
# Uso:
#   ./scripts/upload_model_to_s3.sh <archivo_local> <ruta_destino_en_bucket>
#   ./scripts/upload_model_to_s3.sh backend/ml/artifacts/regressors/hybrid.pt \
#       regression/hybrid/v0.4.1/hybrid.pt

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Uso: $0 <archivo_local> <ruta_en_bucket>" >&2
  exit 1
fi

SRC="$1"
DST="$2"
ENDPOINT="${AWS_S3_ENDPOINT_URL:-}"
BUCKET="${S3_MODELS_BUCKET:-cacaoscan-models}"

AWS_ARGS=()
if [[ -n "$ENDPOINT" ]]; then
  AWS_ARGS+=(--endpoint-url "$ENDPOINT")
fi

echo "→ Subiendo $SRC → s3://$BUCKET/$DST"
aws s3 cp "$SRC" "s3://$BUCKET/$DST" "${AWS_ARGS[@]}"
echo "✓ Subido."
