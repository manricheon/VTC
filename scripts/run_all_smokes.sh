#!/usr/bin/env bash
# Run all currently safe bridge-core smoke examples.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"
mkdir -p "${UV_CACHE_DIR}"

echo "Running bridge-core setup and tests"
bash "${VTC_ROOT}/scripts/setup_bridge_core.sh"

cd "${VTC_ROOT}/envs/bridge-core"

echo
echo "Running Project A codec synthetic smoke"
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py

echo
echo "Running Project B OV-direct synthetic smoke"
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py

if [[ -f ../../projects/gaze-ov-bridge/scripts/smoke_project_a_llava_boundary.py ]]; then
  echo
  echo "Running Project A LLaVA boundary smoke"
  uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_llava_boundary.py
fi

if [[ -f ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_boundary.py ]]; then
  echo
  echo "Running Project B OV boundary smoke"
  uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_boundary.py
fi

if [[ -f ../../projects/projector-eval-harness/scripts/smoke_projector_eval_synthetic.py ]]; then
  echo
  echo "Running projector eval synthetic smoke"
  uv run python ../../projects/projector-eval-harness/scripts/smoke_projector_eval_synthetic.py
fi

cd "${VTC_ROOT}"

echo
echo "Smoke outputs:"
echo "- projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/"
echo "- projects/gaze-ov-bridge/out/smoke_project_a_llava_boundary/"
echo "- projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/"
echo "- projects/gaze-ov-bridge/out/smoke_project_b_ov_boundary/"
echo "- projects/projector-eval-harness/out/smoke_projector_eval_synthetic/"
echo
echo "No model inference was run."
