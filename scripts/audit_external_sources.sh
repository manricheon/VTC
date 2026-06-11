#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${VTC_ROOT}"

count_matches() {
  local path="$1"
  local pattern="$2"
  if [[ ! -d "${path}" ]]; then
    printf '0'
    return
  fi
  if command -v rg >/dev/null 2>&1; then
    rg -n --hidden --glob '!.git' "${pattern}" "${path}" 2>/dev/null | wc -l | tr -d ' '
  else
    grep -RIn "${pattern}" "${path}" 2>/dev/null | wc -l | tr -d ' '
  fi
}

git_field() {
  local path="$1"
  local field="$2"
  if [[ ! -d "${path}/.git" ]]; then
    printf 'not-a-git-repo'
    return
  fi
  case "${field}" in
    remote)
      git -C "${path}" remote get-url origin 2>/dev/null || printf 'unknown'
      ;;
    branch)
      git -C "${path}" branch --show-current 2>/dev/null || printf 'unknown'
      ;;
    commit)
      git -C "${path}" rev-parse --short HEAD 2>/dev/null || printf 'unknown'
      ;;
    *)
      printf 'unknown'
      ;;
  esac
}

print_source() {
  local label="$1"
  local path="$2"
  local purpose="$3"

  echo
  echo "== ${label} =="
  echo "path: ${path}"
  echo "purpose: ${purpose}"
  if [[ -d "${path}" ]]; then
    echo "status: present"
    echo "size: $(du -sh "${path}" 2>/dev/null | awk '{print $1}')"
    echo "remote: $(git_field "${path}" remote)"
    echo "branch: $(git_field "${path}" branch)"
    echo "commit: $(git_field "${path}" commit)"
  else
    echo "status: missing"
    return
  fi

  echo "attention matches:"
  for pattern in flash_attn flash_attention flash_attention_2 attn_implementation sdpa eager; do
    echo "  ${pattern}: $(count_matches "${path}" "${pattern}")"
  done

  echo "integration/profiling matches:"
  for pattern in codec image_grid_thw patch_positions visible_indices llava_onevision2 profile latency memory token max_memory; do
    echo "  ${pattern}: $(count_matches "${path}" "${pattern}")"
  done
}

echo "External source audit"
echo "root: ${VTC_ROOT}"
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

print_source "AutoGaze" "external/AutoGaze" "AutoGaze output generation source inspection"
print_source "LLaVA-OneVision-2" "external/LLaVA-OneVision-2" "LLaVA-OV2 runtime and codec/backend source inspection"
print_source "lmms-eval" "external/lmms-eval" "LLaVA-OV2 evaluation wrapper source inspection"
print_source "LLaVA-OV2 HF code snapshot" "external/LLaVA-OneVision-2-8B-Instruct-code" "HF custom-code snapshot inspection"
print_source "OneVision-Encoder" "external/OneVision-Encoder" "OV-Encoder code/config inspection"
