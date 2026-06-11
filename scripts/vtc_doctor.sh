#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${VTC_ROOT}"

broken=0

section() {
  printf '\n== %s ==\n' "$1"
}

check_path() {
  local path="$1"
  if [[ -e "${path}" ]]; then
    echo "[ok] ${path}"
  else
    echo "[missing] ${path}"
    broken=1
  fi
}

cmd_status() {
  local cmd="$1"
  if command -v "${cmd}" >/dev/null 2>&1; then
    printf '[ok] %s: %s\n' "${cmd}" "$(command -v "${cmd}")"
  else
    printf '[missing] %s\n' "${cmd}"
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

section "Git"
echo "branch: $(git branch --show-current 2>/dev/null || echo unknown)"
echo "head: $(git log --oneline --max-count=1 2>/dev/null || echo unknown)"
echo "status:"
git status --short || true

section "Platform"
uname -a || true
if [[ -f /etc/os-release ]]; then
  sed -n '1,8p' /etc/os-release
elif command -v sw_vers >/dev/null 2>&1; then
  sw_vers
else
  echo "os-release/sw_vers unavailable"
fi

section "Commands"
cmd_status bash
cmd_status uv
cmd_status git
cmd_status curl
cmd_status python
cmd_status python3
cmd_status ffmpeg
if command -v ffmpeg >/dev/null 2>&1; then
  ffmpeg -version 2>/dev/null | head -n 1 || true
fi

section "HF Cache Policy"
if [[ -f "${VTC_ROOT}/scripts/env_weights.sh" ]]; then
  # shellcheck disable=SC1091
  source "${VTC_ROOT}/scripts/env_weights.sh" >/dev/null
fi
echo "HF_HOME=${HF_HOME:-not set}"
echo "HF_HUB_CACHE=${HF_HUB_CACHE:-not set}"
if [[ -n "${HF_TOKEN:-}" ]]; then
  echo "HF_TOKEN=present (value hidden)"
else
  echo "HF_TOKEN=not set"
fi

section "Core Structure"
for path in \
  README.md \
  docs/public \
  scripts \
  envs/bridge-core/pyproject.toml \
  projects/gaze-ov-bridge/pyproject.toml \
  projects/gaze-ov-bridge/src/gaze_ov_bridge \
  projects/gaze-ov-bridge/tests; do
  check_path "${path}"
done

section "External Sources"
for path in \
  external/AutoGaze \
  external/LLaVA-OneVision-2 \
  external/LLaVA-OneVision-2-8B-Instruct-code \
  external/OneVision-Encoder \
  external/lmms-eval; do
  if [[ -d "${path}" ]]; then
    echo "[present] ${path}"
  else
    echo "[missing] ${path}"
  fi
done

section "Checkpoint Directories"
for path in \
  weights/checkpoints/AutoGaze \
  weights/checkpoints/onevision-encoder-large \
  weights/checkpoints/LLaVA-OneVision-2-8B-Instruct; do
  echo "${path}: $(dir_size "${path}")"
done

section "Artifacts"
if compgen -G "artifacts/profiles/*.json" >/dev/null 2>&1; then
  echo "profiles: present"
else
  echo "profiles: none"
fi
if [[ -f "projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/profile.json" ]]; then
  echo "Project A smoke profile: present"
else
  echo "Project A smoke profile: missing"
fi
if [[ -f "projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json" ]]; then
  echo "Project B smoke profile: present"
else
  echo "Project B smoke profile: missing"
fi

section "Env Lock Status"
for env_dir in envs/bridge-core envs/hf-tools envs/autogaze envs/ov-encoder envs/llava-ov2 envs/lmms-eval envs/mps-probe; do
  if [[ -f "${env_dir}/uv.lock" ]]; then
    echo "[lock] ${env_dir}/uv.lock"
  else
    echo "[no-lock] ${env_dir}/uv.lock"
  fi
done

exit "${broken}"
