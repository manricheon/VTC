#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"
mkdir -p "${UV_CACHE_DIR}"

section() {
  printf '\n== %s ==\n' "$1"
}

section "Simplicity Gate"
echo "root=${VTC_ROOT}"
echo "branch=$(cd "${VTC_ROOT}" && git branch --show-current 2>/dev/null || echo unknown)"
echo "head=$(cd "${VTC_ROOT}" && git log --oneline --max-count=1 2>/dev/null || echo unknown)"

section "Doctor"
bash "${VTC_ROOT}/scripts/vtc_doctor.sh" || true

section "Pre-Worktree Gate"
bash "${VTC_ROOT}/scripts/pre_worktree_gate.sh" || true

section "Bridge-Core Tests"
cd "${VTC_ROOT}/envs/bridge-core"
uv run pytest ../../projects/gaze-ov-bridge/tests
uv run pytest ../../projects/projector-eval-harness/tests

section "Compile"
uv run python -m compileall ../../projects/gaze-ov-bridge/src
uv run python -m compileall ../../projects/projector-eval-harness/src

section "Synthetic Smokes"
if [[ -f "${VTC_ROOT}/projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py" ]]; then
  uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py
else
  echo "Project A smoke script missing"
fi

if [[ -f "${VTC_ROOT}/projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py" ]]; then
  uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py
else
  echo "Project B smoke script missing"
fi

if [[ -f "${VTC_ROOT}/projects/projector-eval-harness/scripts/smoke_projector_eval_synthetic.py" ]]; then
  uv run python ../../projects/projector-eval-harness/scripts/smoke_projector_eval_synthetic.py
else
  echo "Projector eval smoke script missing"
fi

section "Projector Eval Source Audit"
cd "${VTC_ROOT}"
bash "${VTC_ROOT}/scripts/audit_projector_sources.sh"

section "Projector Eval Dry-Run"
bash "${VTC_ROOT}/scripts/run_projector_eval_limit1.sh"

section "Profile Summary"
cd "${VTC_ROOT}/envs/bridge-core"
if [[ -f "${VTC_ROOT}/scripts/profile_summary.py" ]]; then
  uv run python ../../scripts/profile_summary.py \
    ../../projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/profile.json \
    ../../projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json \
    ../../projects/projector-eval-harness/out/smoke_projector_eval_synthetic/profile.json || true
else
  echo "profile_summary.py missing"
fi

section "Summary"
echo "simplicity_gate=complete"
echo "downloads=not_run"
echo "external_clones=not_run"
echo "model_inference=not_run"
