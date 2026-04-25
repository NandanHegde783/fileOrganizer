#!/usr/bin/env bash
# run.sh — Run the fileOrganizer container against a host directory.
#
# Usage:
#   bash run.sh [HOST_DIR] [OPTIONS]
#
# Arguments:
#   HOST_DIR   Absolute path to the directory you want to organise.
#              Defaults to the current working directory.
#
# All extra OPTIONS are passed directly to the Python CLI, e.g.:
#   bash run.sh ~/Downloads --dry-run
#   bash run.sh ~/Downloads --recursive --copy
#   bash run.sh ~/Downloads --detect-dupes
#   bash run.sh ~/Downloads --delete-dupes
#   bash run.sh ~/Downloads --undo
#   bash run.sh ~/Downloads --schedule daily
#
# The container is automatically removed after each run (--rm).
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
IMAGE_NAME="file-organizer"
IMAGE_TAG="latest"

# ── Ensure we cd to project root so paths are predictable ─────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# ── Parse HOST_DIR (first positional arg, if it looks like a path) ────────────
HOST_DIR="${PWD}"   # default: current directory
EXTRA_ARGS=()

if [[ $# -ge 1 && "$1" != --* ]]; then
    HOST_DIR="$(cd "$1" && pwd)"   # resolve to absolute path
    shift
fi

# Remaining args are forwarded straight to the Python CLI
EXTRA_ARGS=("$@")

# ── Sanity checks ─────────────────────────────────────────────────────────────
if [[ ! -d "${HOST_DIR}" ]]; then
    echo "❌  Error: '${HOST_DIR}' is not a directory or does not exist." >&2
    exit 1
fi

echo "============================================"
echo "  Image    : ${IMAGE_NAME}:${IMAGE_TAG}"
echo "  Target   : ${HOST_DIR}"
if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    echo "  Options  : ${EXTRA_ARGS[*]}"
fi
echo "============================================"
echo ""

docker run \
  --rm \
  --interactive \
  --tty \
  --volume "${HOST_DIR}:/data" \
  "${IMAGE_NAME}:${IMAGE_TAG}" \
  "${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}"
