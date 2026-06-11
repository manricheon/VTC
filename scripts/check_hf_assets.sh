#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${VTC_ROOT}/scripts/env_weights.sh" ]]; then
  # shellcheck disable=SC1091
  source "${VTC_ROOT}/scripts/env_weights.sh" >/dev/null
fi

CHECKPOINT_ROOT="${VTC_ROOT}/weights/checkpoints"

file_count() {
  local path="$1"
  if [[ -d "${path}" ]]; then
    find "${path}" -type f | wc -l | tr -d ' '
  else
    printf '0'
  fi
}

payload_count() {
  local path="$1"
  if [[ -d "${path}" ]]; then
    find "${path}" -type f \( \
      -name '*.safetensors' -o \
      -name '*.bin' -o \
      -name '*.pt' -o \
      -name '*.pth' -o \
      -name '*.gguf' -o \
      -name '*.onnx' \
    \) | wc -l | tr -d ' '
  else
    printf '0'
  fi
}

dir_size() {
  local path="$1"
  if [[ -d "${path}" ]]; then
    du -sh "${path}" 2>/dev/null | awk '{print $1}'
  else
    printf 'missing'
  fi
}

asset_status() {
  local path="$1"
  local files payloads
  files="$(file_count "${path}")"
  payloads="$(payload_count "${path}")"
  if [[ ! -d "${path}" ]]; then
    printf 'missing'
  elif [[ "${files}" == "0" ]]; then
    printf 'empty'
  elif [[ "${payloads}" == "0" ]]; then
    printf 'metadata_only'
  else
    printf 'payload_present'
  fi
}

print_asset() {
  local label="$1"
  local repo_id="$2"
  local rel_path="$3"
  local path="${VTC_ROOT}/${rel_path}"
  local status files payloads size
  status="$(asset_status "${path}")"
  files="$(file_count "${path}")"
  payloads="$(payload_count "${path}")"
  size="$(dir_size "${path}")"

  printf '[%s] %s\n' "${status}" "${label}"
  printf '  repo: %s\n' "${repo_id}"
  printf '  path: %s\n' "${rel_path}"
  printf '  files: %s\n' "${files}"
  printf '  payload files: %s\n' "${payloads}"
  printf '  size: %s\n' "${size}"
}

echo "HF asset check"
echo "HF_HOME=${HF_HOME:-not set}"
echo "HF_HUB_CACHE=${HF_HUB_CACHE:-not set}"
if [[ -n "${HF_TOKEN:-}" ]]; then
  echo "HF_TOKEN=present (value hidden)"
else
  echo "HF_TOKEN=not set"
fi
echo

missing_payload=0

print_asset "AutoGaze" "nvidia/AutoGaze" "weights/checkpoints/AutoGaze"
[[ "$(payload_count "${CHECKPOINT_ROOT}/AutoGaze")" != "0" ]] || missing_payload=1
echo

print_asset "OneVision-Encoder" "lmms-lab-encoder/onevision-encoder-large" "weights/checkpoints/onevision-encoder-large"
[[ "$(payload_count "${CHECKPOINT_ROOT}/onevision-encoder-large")" != "0" ]] || missing_payload=1
echo

print_asset "LLaVA-OV2" "lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct" "weights/checkpoints/LLaVA-OneVision-2-8B-Instruct"
[[ "$(payload_count "${CHECKPOINT_ROOT}/LLaVA-OneVision-2-8B-Instruct")" != "0" ]] || missing_payload=1
echo

if [[ "${missing_payload}" == "1" ]]; then
  echo "One or more checkpoint directories do not contain recognized payload files."
  echo "Use scripts/setup_hf_assets.sh with explicit VTC_ALLOW_WEIGHT_DOWNLOAD and target flags to download missing assets."
  if [[ "${REQUIRED_HF_ASSETS:-0}" == "1" ]]; then
    exit 1
  fi
else
  echo "All expected checkpoint directories contain recognized payload files."
fi
