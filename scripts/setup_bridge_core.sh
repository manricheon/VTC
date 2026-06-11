#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OS_NAME="$(uname -s)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"
mkdir -p "${UV_CACHE_DIR}"

if [[ "${OS_NAME}" != "Linux" ]]; then
  echo "Warning: official VTC target is Linux; current OS is ${OS_NAME}."
  if [[ "${ALLOW_NON_LINUX:-0}" == "1" ]]; then
    echo "ALLOW_NON_LINUX=1 set; continuing best-effort."
  elif [[ "${OS_NAME}" == "Darwin" && "${VTC_ALLOW_MPS_PROBE:-0}" == "1" ]]; then
    echo "VTC_ALLOW_MPS_PROBE=1 set on macOS; continuing best-effort."
  elif [[ "${VTC_STRICT_LINUX:-0}" == "1" ]]; then
    echo "VTC_STRICT_LINUX=1 set; refusing non-Linux setup." >&2
    exit 2
  else
    echo "Continuing bridge-core setup because it is pure Python and installs no model stack."
    echo "Set VTC_STRICT_LINUX=1 to make non-Linux hosts fail this script."
  fi
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Run: bash scripts/install_uv_linux.sh" >&2
  exit 1
fi

cd "${VTC_ROOT}/envs/bridge-core"
uv sync --group dev
uv run python -m compileall ../../projects/gaze-ov-bridge/src
uv run pytest -q ../../projects/gaze-ov-bridge/tests
