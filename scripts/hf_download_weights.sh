#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

source "${VTC_ROOT}/scripts/env_weights.sh"

HF_TOOLS_DIR="${VTC_ROOT}/envs/hf-tools"
SNAPSHOT_SCRIPT="../../scripts/hf_download_snapshot.py"
PLAN_SCRIPT="../../scripts/hf_download_plan.py"

print_disk_space() {
  echo "Disk space for weights:"
  df -h "${VTC_ROOT}/weights"
}

run_hf_tool() {
  (
    cd "${HF_TOOLS_DIR}"
    uv run python "$@"
  )
}

print_download_plan() {
  run_hf_tool "${PLAN_SCRIPT}"
}

download_snapshot() {
  local repo_id="$1"
  local local_dir="$2"
  run_hf_tool "${SNAPSHOT_SCRIPT}" \
    --repo-id "${repo_id}" \
    --repo-type model \
    --local-dir "${local_dir}" \
    --cache-dir "${HF_HUB_CACHE}"
}

select_autogaze_repo() {
  local docs_dir="${VTC_ROOT}/external/AutoGaze"
  local selected=""
  local candidates=("nvidia/AutoGaze" "bfshi/AutoGaze")

  if [[ -d "${docs_dir}" ]]; then
    for candidate in "${candidates[@]}"; do
      if grep -Rqs "${candidate}" "${docs_dir}/README.md" "${docs_dir}/QUICK_START.md" "${docs_dir}/INTEGRATION.md" 2>/dev/null; then
        selected="${candidate}"
        break
      fi
    done
  fi

  if [[ -z "${selected}" ]]; then
    cat >&2 <<EOF
Could not identify the correct AutoGaze Hugging Face repo from external/AutoGaze docs.

Candidate order:
  1. nvidia/AutoGaze
  2. bfshi/AutoGaze

Do not guess silently. Inspect external/AutoGaze README/QUICK_START or HF repo files,
then set VTC_AUTOGAZE_REPO=<repo-id> if the correct repo is known.
EOF
    return 2
  fi

  printf '%s\n' "${selected}"
}

print_disk_space

if [[ "${VTC_ALLOW_WEIGHT_DOWNLOAD:-0}" != "1" ]]; then
  cat <<EOF
Weight downloads are disabled.

To enable a specific download, set:
  VTC_ALLOW_WEIGHT_DOWNLOAD=1

and one or more target flags:
  VTC_DOWNLOAD_AUTOGAZE=1
  VTC_DOWNLOAD_OV_ENCODER=1
  VTC_DOWNLOAD_LLAVA_OV2=1

Example:
  VTC_ALLOW_WEIGHT_DOWNLOAD=1 VTC_DOWNLOAD_OV_ENCODER=1 bash scripts/hf_download_weights.sh

Current plan:
EOF
  print_download_plan
  exit 2
fi

if [[ "${VTC_DOWNLOAD_AUTOGAZE:-0}" != "1" && "${VTC_DOWNLOAD_OV_ENCODER:-0}" != "1" && "${VTC_DOWNLOAD_LLAVA_OV2:-0}" != "1" ]]; then
  echo "No specific download target selected."
  print_download_plan
  exit 0
fi

run_hf_tool "../../scripts/hf_auth_check.py" --public-only-ok

if [[ "${VTC_DOWNLOAD_AUTOGAZE:-0}" == "1" ]]; then
  repo_id="${VTC_AUTOGAZE_REPO:-}"
  if [[ -z "${repo_id}" ]]; then
    repo_id="$(select_autogaze_repo)"
  fi
  echo "Downloading AutoGaze candidate repo: ${repo_id}"
  download_snapshot "${repo_id}" "${VTC_ROOT}/weights/checkpoints/AutoGaze"
fi

if [[ "${VTC_DOWNLOAD_OV_ENCODER:-0}" == "1" ]]; then
  echo "Downloading OneVision-Encoder weights"
  download_snapshot \
    "lmms-lab-encoder/onevision-encoder-large" \
    "${VTC_ROOT}/weights/checkpoints/onevision-encoder-large"
fi

if [[ "${VTC_DOWNLOAD_LLAVA_OV2:-0}" == "1" ]]; then
  echo "Downloading LLaVA-OV2 weights"
  download_snapshot \
    "lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct" \
    "${VTC_ROOT}/weights/checkpoints/LLaVA-OneVision-2-8B-Instruct"
fi

echo "Requested weight download commands completed."
