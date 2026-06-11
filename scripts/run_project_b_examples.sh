#!/usr/bin/env bash
# Run safe Project B examples only.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"
mkdir -p "${UV_CACHE_DIR}"

cd "${VTC_ROOT}/envs/bridge-core"

uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py

if [[ -f ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_boundary.py ]]; then
  uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_boundary.py
fi

cd "${VTC_ROOT}"

echo "Project B profile paths:"
echo "- projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json"
echo "- projects/gaze-ov-bridge/out/smoke_project_b_ov_boundary/profile.json"
echo "No OV-Encoder forward was run."
