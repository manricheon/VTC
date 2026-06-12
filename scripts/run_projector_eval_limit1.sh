#!/usr/bin/env bash
# Guarded lmms-eval --limit runner for LLaVA-1.5 projector comparisons.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PROJECT_SRC="${VTC_ROOT}/projects/projector-eval-harness/src"
LMMS_ROOT="${VTC_ROOT}/external/lmms-eval"
PROFILE_ROOT="${VTC_ROOT}/artifacts/profiles"
INCLUDE_PATH="${VTC_ROOT}/projects/projector-eval-harness/tasks"

PROJECTOR_MODEL="${PROJECTOR_MODEL:-all}"
TASK="${TASK:-mme}"
LIMIT="${LIMIT:-1}"
NPROC="${NPROC:-1}"
PORT="${PORT:-29840}"
DEVICE_MAP="${DEVICE_MAP:-auto}"
FOURIER_RESERVE="${FOURIER_RESERVE:-12}"
DIVT_THRESHOLD="${DIVT_THRESHOLD:-0.65}"
FOURIER_CKPT="${FOURIER_CKPT:-${VTC_ROOT}/weights/checkpoints/llava-v1.5-7b}"
DIVT_CKPT="${DIVT_CKPT:-${VTC_ROOT}/weights/checkpoints/llava-v1.5-divt-0.65-7b}"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"

LIMIT_ARGS=()
case "${LIMIT}" in
  none|all|full)
    LIMIT_LABEL="full"
    ;;
  ''|*[!0-9]*)
    echo "LIMIT must be a positive integer, none, all, or full" >&2
    exit 2
    ;;
  *)
    if (( LIMIT <= 0 )); then
      echo "LIMIT must be a positive integer, none, all, or full" >&2
      exit 2
    fi
    LIMIT_ARGS=("--limit" "${LIMIT}")
    LIMIT_LABEL="limit${LIMIT}"
    ;;
esac
RUN_ID="${RUN_ID:-${LIMIT_LABEL}_${TASK}}"

models=()
case "${PROJECTOR_MODEL}" in
  all)
    models=("fourier" "divt")
    ;;
  fourier|divt)
    models=("${PROJECTOR_MODEL}")
    ;;
  *)
    echo "PROJECTOR_MODEL must be one of: all, fourier, divt" >&2
    exit 2
    ;;
esac

print_command() {
  local label="$1"
  local env_dir="$2"
  local model_name="$3"
  local model_args="$4"
  local out_dir="$5"

  echo
  echo "== ${label} =="
  echo "env_dir=${env_dir}"
  echo "model=${model_name}"
  echo "task=${TASK}"
  echo "limit=${LIMIT_LABEL}"
  echo "out_dir=${out_dir}"
  echo "planned command:"
  echo "cd ${env_dir}"
  local limit_fragment=""
  if (( ${#LIMIT_ARGS[@]} > 0 )); then
    limit_fragment=" ${LIMIT_ARGS[*]}"
  fi
  echo "LMMS_EVAL_PLUGINS=vtc_projector_eval PYTHONPATH=${PROJECT_SRC}:${LMMS_ROOT}:\${PYTHONPATH:-} uv run accelerate launch --num_processes=${NPROC} --main_process_port=${PORT} -m lmms_eval --model ${model_name} --model_args '${model_args}' --tasks ${TASK} --batch_size 1${limit_fragment} --include_path '${INCLUDE_PATH}' --log_samples --output_path '${out_dir}/'"
}

run_one() {
  local label="$1"
  local env_dir="$2"
  local model_name="$3"
  local model_args="$4"
  local out_dir="$5"
  shift 5
  local blockers=("$@")

  print_command "${label}" "${env_dir}" "${model_name}" "${model_args}" "${out_dir}"
  if (( ${#blockers[@]} > 0 )); then
    echo "blockers:"
    for blocker in "${blockers[@]}"; do
      echo "- ${blocker}"
    done
  fi

  if [[ "${RUN_PROJECTOR_EVAL:-0}" != "1" ]]; then
    echo "RUN_PROJECTOR_EVAL is not 1; dry-run only."
    return
  fi
  if (( ${#blockers[@]} > 0 )); then
    echo "Refusing to run ${label} while blockers remain." >&2
    exit 1
  fi

  mkdir -p "${out_dir}"
  cd "${env_dir}"
  export LMMS_EVAL_PLUGINS=vtc_projector_eval
  export PYTHONPATH="${PROJECT_SRC}:${LMMS_ROOT}:${PYTHONPATH:-}"
  export VTC_PROJECTOR_PROFILE_JSONL="${PROFILE_ROOT}/projector_eval_${RUN_ID}.jsonl"
  uv run accelerate launch \
    --num_processes="${NPROC}" \
    --main_process_port="${PORT}" \
    -m lmms_eval \
    --model "${model_name}" \
    --model_args "${model_args}" \
    --tasks "${TASK}" \
    --batch_size 1 \
    "${LIMIT_ARGS[@]}" \
    --include_path "${INCLUDE_PATH}" \
    --log_samples \
    --output_path "${out_dir}/" \
    2>&1 | tee "${out_dir}/run.log"
}

echo "projector eval lmms-eval guarded runner"
echo "VTC_ROOT=${VTC_ROOT}"
echo "PROJECTOR_MODEL=${PROJECTOR_MODEL}"
echo "TASK=${TASK}"
echo "LIMIT=${LIMIT}"

for model in "${models[@]}"; do
  blockers=()
  if [[ ! -d "${LMMS_ROOT}" ]]; then
    blockers+=("missing external/lmms-eval")
  fi
  if [[ ! -d "${PROJECT_SRC}" ]]; then
    blockers+=("missing projector eval package source")
  fi

  if [[ "${model}" == "fourier" ]]; then
    env_dir="${VTC_ROOT}/envs/fourier-llava15-eval"
    if [[ ! -d "${VTC_ROOT}/external/Fourier-Compressor" ]]; then
      blockers+=("missing external/Fourier-Compressor")
    fi
    if [[ ! -d "${FOURIER_CKPT}" ]]; then
      blockers+=("missing Fourier/LLaVA-1.5 checkpoint directory: ${FOURIER_CKPT}")
    fi
    run_one \
      "fourier" \
      "${env_dir}" \
      "vtc_fourier_llava15" \
      "pretrained=${FOURIER_CKPT},device_map=${DEVICE_MAP},use_flash_attention_2=False,fourier_reserve=${FOURIER_RESERVE}" \
      "${PROFILE_ROOT}/projector_eval_${RUN_ID}_fourier_${TASK}" \
      "${blockers[@]}"
  else
    env_dir="${VTC_ROOT}/envs/divt-llava15-eval"
    if [[ ! -d "${VTC_ROOT}/external/DiVT" ]]; then
      blockers+=("missing external/DiVT")
    fi
    if [[ ! -d "${DIVT_CKPT}" ]]; then
      blockers+=("missing DiVT checkpoint directory: ${DIVT_CKPT}")
    fi
    run_one \
      "divt" \
      "${env_dir}" \
      "vtc_divt_llava15" \
      "pretrained=${DIVT_CKPT},device_map=${DEVICE_MAP},use_flash_attention_2=False,divt_threshold=${DIVT_THRESHOLD}" \
      "${PROFILE_ROOT}/projector_eval_${RUN_ID}_divt_${TASK}" \
      "${blockers[@]}"
  fi
done
