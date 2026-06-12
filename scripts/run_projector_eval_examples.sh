#!/usr/bin/env bash
# Run safe projector-eval examples only.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"
mkdir -p "${UV_CACHE_DIR}"

echo "Running bridge-core setup and tests"
bash "${VTC_ROOT}/scripts/setup_bridge_core.sh"

echo
echo "Auditing projector external sources"
bash "${VTC_ROOT}/scripts/audit_projector_sources.sh"

cd "${VTC_ROOT}/envs/bridge-core"

echo
echo "Running projector eval synthetic smoke"
uv run python ../../projects/projector-eval-harness/scripts/smoke_projector_eval_synthetic.py

cd "${VTC_ROOT}"

echo
echo "Running guarded projector eval dry-run"
bash "${VTC_ROOT}/scripts/run_projector_eval_limit1.sh"

echo
echo "Projector eval profile paths:"
echo "- projects/projector-eval-harness/out/smoke_projector_eval_synthetic/profile.json"
echo "- projects/projector-eval-harness/out/smoke_projector_eval_synthetic/report.md"
echo "No checkpoint download, dataset access, CUDA runtime, or model inference was run."
