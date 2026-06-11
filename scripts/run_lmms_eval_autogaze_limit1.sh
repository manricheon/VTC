#!/usr/bin/env bash
# Guarded lmms-eval --limit 1 runner skeleton for future autogaze codec work.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

source "${VTC_ROOT}/scripts/env_weights.sh"

LMMS_ROOT="${VTC_ROOT}/external/lmms-eval"
LMMS_ENV="${VTC_ROOT}/envs/lmms-eval"
LLAVA_CKPT="${VTC_ROOT}/weights/checkpoints/LLaVA-OneVision-2-8B-Instruct"
PROJECT_A_BOUNDARY_DOC="${VTC_ROOT}/docs/public/project_a_llava_boundary.md"
PROJECT_A_BOUNDARY_PROFILE="${VTC_ROOT}/projects/gaze-ov-bridge/out/smoke_project_a_llava_boundary/profile.json"
PROFILE_ROOT="${VTC_ROOT}/artifacts/profiles"

TASK="${TASK:-JumpScore}"
TC="${TC:-128}"
TS="${TS:-2}"
MIN_PX="${MIN_PX:-100352}"
MAX_PX="${MAX_PX:-313600}"
PORT="${PORT:-29830}"
NPROC="${NPROC:-1}"
ATTN_IMPLEMENTATION="${ATTN_IMPLEMENTATION:-flash_attention_2}"
OUT_DIR="${PROFILE_ROOT}/lmms_eval_limit1_${TASK}_codec_tc${TC}"

blockers=()

if [[ ! -d "${LMMS_ROOT}" ]]; then
  blockers+=("missing external/lmms-eval")
fi
if [[ ! -d "${LMMS_ENV}" ]]; then
  blockers+=("missing envs/lmms-eval")
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
  blockers+=("missing ffmpeg")
fi
if [[ ! -d "${LLAVA_CKPT}" ]]; then
  blockers+=("missing LLaVA-OV2 checkpoint directory")
elif ! find "${LLAVA_CKPT}" -maxdepth 1 -type f \( -name '*.safetensors' -o -name 'config.json' \) | grep -q .; then
  blockers+=("LLaVA-OV2 checkpoint directory has no config/weight files")
fi
if [[ ! -f "${PROJECT_A_BOUNDARY_DOC}" ]]; then
  blockers+=("missing Project A boundary doc")
fi
if [[ ! -f "${PROJECT_A_BOUNDARY_PROFILE}" ]]; then
  blockers+=("missing Project A boundary smoke profile; run smoke_project_a_llava_boundary.py")
fi

MODEL_ARGS="pretrained=${LLAVA_CKPT},trust_remote_code=True,attn_implementation=${ATTN_IMPLEMENTATION},messages_format=timestamp,timestamp_decimals=${TS},fps=1,max_num_frames=${TC},min_pixels=${MIN_PX},max_pixels=${MAX_PX},video_backend=codec,codec_target_canvas=${TC}"

echo "lmms-eval autogaze codec --limit 1 plan"
echo "VTC_ROOT=${VTC_ROOT}"
echo "TASK=${TASK}"
echo "TC=${TC}"
echo "ATTN_IMPLEMENTATION=${ATTN_IMPLEMENTATION}"
echo "OUT_DIR=${OUT_DIR}"
echo
echo "Planned command:"
echo "cd ${LMMS_ENV}"
echo "PYTHONPATH=${LMMS_ROOT}:\${PYTHONPATH:-} uv run accelerate launch --num_processes=${NPROC} --main_process_port=${PORT} -m lmms_eval --model llava_onevision2 --model_args '${MODEL_ARGS}' --tasks ${TASK} --batch_size 1 --limit 1 --log_samples --output_path '${OUT_DIR}/'"

if (( ${#blockers[@]} > 0 )); then
  echo
  echo "Blockers:"
  for blocker in "${blockers[@]}"; do
    echo "- ${blocker}"
  done
fi

if [[ "${RUN_LMMS_EVAL:-0}" != "1" ]]; then
  echo
  echo "RUN_LMMS_EVAL is not 1; dry-run only."
  echo "To execute after blockers are resolved:"
  echo "RUN_LMMS_EVAL=1 TASK=${TASK} TC=${TC} TS=${TS} bash scripts/run_lmms_eval_autogaze_limit1.sh"
  exit 0
fi

if (( ${#blockers[@]} > 0 )); then
  echo "Refusing to run lmms-eval while blockers remain." >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"
cd "${LMMS_ENV}"
export PYTHONPATH="${LMMS_ROOT}:${PYTHONPATH:-}"
export TOKENIZERS_PARALLELISM=false
export LLAVA_CODEC_ONLINE_TUNED="${LLAVA_CODEC_ONLINE_TUNED:-1}"

uv run accelerate launch \
  --num_processes="${NPROC}" \
  --main_process_port="${PORT}" \
  -m lmms_eval \
  --model llava_onevision2 \
  --model_args "${MODEL_ARGS}" \
  --tasks "${TASK}" \
  --batch_size 1 \
  --limit 1 \
  --log_samples \
  --output_path "${OUT_DIR}/" \
  2>&1 | tee "${OUT_DIR}/run.log"
