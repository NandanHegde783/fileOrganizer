#!/usr/bin/env bash
#!/usr/bin/env bash
# build.sh — Build the fileOrganizer Docker image.
# Run from the project root:  bash build.sh [IMAGE_TAG]
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
IMAGE_NAME="file-organizer"
IMAGE_TAG="${1:-latest}"
FULL_TAG="${IMAGE_NAME}:${IMAGE_TAG}"

# ── Ensure we are in the project root (where Dockerfile lives) ────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "============================================"
echo "  Building Docker image: ${FULL_TAG}"
echo "  Context: ${SCRIPT_DIR}"
echo "============================================"

docker build \
  --tag "${FULL_TAG}" \
  --file Dockerfile \
  .

echo ""
echo "✅  Build complete → ${FULL_TAG}"
echo "    Run with: bash run.sh [HOST_DIR] [OPTIONS]"
