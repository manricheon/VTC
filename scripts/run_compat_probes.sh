#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RUN_UV_PROBES="${RUN_UV_PROBES:-0}"
RUN_OPTIONAL_MPS="${RUN_OPTIONAL_MPS:-0}"

cat <<EOF
Compatibility probes are isolated by environment.

Default mode prints commands only and does not sync or install dependencies.
Set RUN_UV_PROBES=1 to run with 'uv run --no-sync' in each existing env.
Set RUN_OPTIONAL_MPS=1 to include the optional Mac/MPS probe.

EOF

run_or_print() {
  local env_dir="$1"
  local script_path="$2"
  local label="$3"

  local command="cd ${env_dir} && uv run --no-sync python ../../${script_path}"
  if [[ "${RUN_UV_PROBES}" != "1" ]]; then
    printf '[dry-run] %s: %s\n' "${label}" "${command}"
    return 0
  fi

  printf '[run] %s\n' "${label}"
  (
    cd "${VTC_ROOT}/${env_dir}"
    uv run --no-sync python "../../${script_path}"
  )
}

run_or_print "envs/autogaze" "scripts/probe_autogaze_env.py" "AutoGaze"
run_or_print "envs/ov-encoder" "scripts/probe_ov_encoder_env.py" "OneVision-Encoder"
run_or_print "envs/llava-ov2" "scripts/probe_llava_ov2_env.py" "LLaVA-OV2"
run_or_print "envs/lmms-eval" "scripts/probe_lmms_eval_env.py" "lmms-eval"

if [[ "${RUN_OPTIONAL_MPS}" == "1" ]]; then
  run_or_print "envs/mps-probe" "scripts/probe_mps_env.py" "MPS probe"
else
  echo "[skip] MPS probe is optional; set RUN_OPTIONAL_MPS=1 to include it."
fi
