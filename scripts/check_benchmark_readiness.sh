#!/usr/bin/env bash
# Check whether the lmms-eval benchmark path is ready to attempt --limit 1.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ready=1

check_path() {
  local label="$1"
  local path="$2"
  if [[ -e "${VTC_ROOT}/${path}" ]]; then
    echo "[ok] ${label}: ${path}"
  else
    echo "[missing] ${label}: ${path}"
    ready=0
  fi
}

echo "Benchmark readiness check"
echo "root=${VTC_ROOT}"

check_path "lmms-eval source" "external/lmms-eval"
check_path "LLaVA-OneVision-2 source" "external/LLaVA-OneVision-2"
check_path "LLaVA-OV2 checkpoint" "weights/checkpoints/LLaVA-OneVision-2-8B-Instruct"
check_path "lmms-eval env" "envs/lmms-eval"
check_path "limit-one runner" "scripts/run_lmms_eval_autogaze_limit1.sh"
check_path "Project A boundary smoke" "projects/gaze-ov-bridge/scripts/smoke_project_a_llava_boundary.py"
check_path "Project A boundary doc" "docs/public/project_a_llava_boundary.md"

if command -v ffmpeg >/dev/null 2>&1; then
  echo "[ok] ffmpeg: $(command -v ffmpeg)"
else
  echo "[missing] ffmpeg"
  ready=0
fi

if [[ -d "${VTC_ROOT}/weights/checkpoints/LLaVA-OneVision-2-8B-Instruct" ]]; then
  if find "${VTC_ROOT}/weights/checkpoints/LLaVA-OneVision-2-8B-Instruct" -maxdepth 1 -type f \( -name '*.safetensors' -o -name 'config.json' \) | grep -q .; then
    echo "[ok] LLaVA-OV2 checkpoint payload files present"
  else
    echo "[missing] LLaVA-OV2 checkpoint payload files"
    ready=0
  fi
fi

if [[ -f "${VTC_ROOT}/projects/gaze-ov-bridge/out/smoke_project_a_llava_boundary/profile.json" ]]; then
  echo "[ok] Project A boundary profile present"
else
  echo "[missing] Project A boundary profile; run: bash scripts/run_project_a_examples.sh"
  ready=0
fi

if [[ "${ready}" == "1" ]]; then
  echo "READY_FOR_BENCHMARK=1"
else
  echo "READY_FOR_BENCHMARK=0"
fi

exit 0
