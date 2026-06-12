#!/usr/bin/env bash
# Summarize known smoke profiles when present.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"
mkdir -p "${UV_CACHE_DIR}"

profiles=(
  "projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/profile.json"
  "projects/gaze-ov-bridge/out/smoke_project_a_llava_boundary/profile.json"
  "projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json"
  "projects/gaze-ov-bridge/out/smoke_project_b_ov_boundary/profile.json"
  "projects/projector-eval-harness/out/smoke_projector_eval_synthetic/profile.json"
)

existing=()
for profile in "${profiles[@]}"; do
  if [[ -f "${VTC_ROOT}/${profile}" ]]; then
    existing+=("${profile}")
  else
    echo "Skipping missing profile: ${profile}"
  fi
done

if (( ${#existing[@]} == 0 )); then
  echo "No smoke profiles found. Run: bash scripts/run_all_smokes.sh"
  exit 0
fi

cd "${VTC_ROOT}/envs/bridge-core"
args=()
for profile in "${existing[@]}"; do
  args+=("../../${profile}")
done

uv run python ../../scripts/profile_summary.py "${args[@]}"
