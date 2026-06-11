#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"
mkdir -p "${UV_CACHE_DIR}"

ready=1

fail_gate() {
  echo "[fail] $1"
  ready=0
}

pass_gate() {
  echo "[ok] $1"
}

check_file() {
  local path="$1"
  local label="$2"
  if [[ -f "${VTC_ROOT}/${path}" ]]; then
    pass_gate "${label}: ${path}"
  else
    fail_gate "${label} missing: ${path}"
  fi
}

echo "Pre-worktree gate"
echo "branch: $(cd "${VTC_ROOT}" && git branch --show-current)"
echo "head: $(cd "${VTC_ROOT}" && git log --oneline --max-count=1)"

if (
  cd "${VTC_ROOT}/envs/bridge-core"
  uv run pytest ../../projects/gaze-ov-bridge/tests
); then
  pass_gate "bridge-core tests"
else
  fail_gate "bridge-core tests"
fi

if (
  cd "${VTC_ROOT}/envs/bridge-core"
  uv run python "../../projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py"
); then
  pass_gate "Project A synthetic smoke"
else
  fail_gate "Project A synthetic smoke"
fi

if (
  cd "${VTC_ROOT}/envs/bridge-core"
  uv run python "../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py"
); then
  pass_gate "Project B synthetic smoke"
else
  fail_gate "Project B synthetic smoke"
fi

check_file "projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/profile.json" "Project A profile"
check_file "projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json" "Project B profile"
check_file "docs/public/blocker_resolution_status.md" "blocker status doc"
check_file "docs/public/weights_snapshot.md" "weights status doc"
check_file "docs/public/system_dependencies.md" "system dependency status doc"
check_file "docs/public/model_env_status.md" "model env status doc"
check_file "docs/public/attention_backend_status.md" "attention backend status doc"
check_file "docs/public/hf_access_status.md" "HF access status doc"

if [[ -d "${VTC_ROOT}/external/AutoGaze" && -d "${VTC_ROOT}/external/LLaVA-OneVision-2" && -d "${VTC_ROOT}/external/OneVision-Encoder" ]]; then
  pass_gate "external source status known"
else
  fail_gate "required external source path missing"
fi

if command -v ffmpeg >/dev/null 2>&1; then
  pass_gate "ffmpeg available"
else
  echo "[deferred] ffmpeg missing or unverified; codec/backend runtime remains blocked but documented."
fi

if [[ "${ready}" == "1" ]]; then
  echo "READY_FOR_WORKTREE=1"
  exit 0
fi

echo "READY_FOR_WORKTREE=0"
exit 1
