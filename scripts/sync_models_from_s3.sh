#!/usr/bin/env bash
# Sincroniza modelos entrenados (.pt/.pth) desde el bucket S3/MinIO de modelos
# hacia backend/ml/artifacts/ para poder correr inferencia en local sin
# reentrenar. Por defecto apunta a MinIO local.
#
# Uso:
#   AWS_S3_ENDPOINT_URL=http://localhost:19000 \
#   S3_MODELS_BUCKET=cacaoscan-models \
#   AWS_ACCESS_KEY_ID=minioadmin AWS_SECRET_ACCESS_KEY=minioadmin123 \
#   ./scripts/sync_models_from_s3.sh
#
# Para producción AWS real, omite AWS_S3_ENDPOINT_URL.

set -euo pipefail

ENDPOINT="${AWS_S3_ENDPOINT_URL:-}"
BUCKET="${S3_MODELS_BUCKET:-cacaoscan-models}"
DEST="${MODELS_DEST:-backend/ml/artifacts}"

mkdir -p "$DEST"

AWS_ARGS=()
if [[ -n "$ENDPOINT" ]]; then
  AWS_ARGS+=(--endpoint-url "$ENDPOINT")
fi

echo "→ Sincronizando s3://$BUCKET/ → $DEST  (endpoint=${ENDPOINT:-AWS})"
aws s3 sync "s3://$BUCKET/" "$DEST/" "${AWS_ARGS[@]}" \
  --exclude "*" \
  --include "*.pt" --include "*.pth" --include "*.pkl" --include "manifest.json"

echo "✓ Modelos sincronizados."
