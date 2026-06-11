#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SUMMARY_PATH="${VTC_ROOT}/artifacts/compat/model_envs_best_effort.json"
SUMMARY_TMP="${SUMMARY_PATH}.jsonl"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"
mkdir -p "${UV_CACHE_DIR}" "${VTC_ROOT}/artifacts/compat"
: > "${SUMMARY_TMP}"

if [[ -f "${VTC_ROOT}/scripts/env_weights.sh" ]]; then
  # shellcheck disable=SC1091
  source "${VTC_ROOT}/scripts/env_weights.sh" >/dev/null
fi

write_record() {
  local env_name="$1"
  local env_dir="$2"
  local sync_status="$3"
  local probe_status="$4"
  local notes="$5"
  python3 - "$SUMMARY_TMP" "$env_name" "$env_dir" "$sync_status" "$probe_status" "$notes" <<'PY'
import json
import sys
from pathlib import Path

path, env_name, env_dir, sync_status, probe_status, notes = sys.argv[1:]
with Path(path).open("a", encoding="utf-8") as fh:
    fh.write(json.dumps({
        "env_name": env_name,
        "env_dir": env_dir,
        "sync_status": sync_status,
        "probe_status": probe_status,
        "notes": notes,
    }, sort_keys=True) + "\n")
PY
}

aggregate_summary() {
  python3 - "$SUMMARY_TMP" "$SUMMARY_PATH" <<'PY'
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

tmp_path, out_path = map(Path, sys.argv[1:])
records = []
if tmp_path.exists():
    for line in tmp_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
try:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
except Exception:
    head = None
summary = {
    "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "git_commit": head,
    "platform": platform.platform(),
    "heavy_env_sync_allowed": bool(int(__import__("os").environ.get("VTC_ALLOW_HEAVY_ENV_SYNC", "0"))),
    "records": records,
}
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}

run_env() {
  local env_name="$1"
  local env_dir="$2"
  local probe_script="$3"
  local sync_status="skipped"
  local probe_status="skipped"
  local notes=""

  if [[ ! -d "${VTC_ROOT}/${env_dir}" ]]; then
    write_record "${env_name}" "${env_dir}" "missing_env_dir" "skipped" "Environment directory is missing."
    return 0
  fi

  if [[ "${VTC_ALLOW_HEAVY_ENV_SYNC:-0}" != "1" ]]; then
    printf '[skip] %s heavy sync disabled. To run: cd %s && uv sync && uv run python ../../%s\n' "${env_name}" "${env_dir}" "${probe_script}"
    write_record "${env_name}" "${env_dir}" "skipped_by_policy" "skipped_by_policy" "Set VTC_ALLOW_HEAVY_ENV_SYNC=1 to sync and probe this env."
    return 0
  fi

  printf '[sync] %s\n' "${env_name}"
  if (
    cd "${VTC_ROOT}/${env_dir}"
    uv sync
  ); then
    sync_status="pass"
  else
    sync_status="fail"
    notes="uv sync failed; probe still attempted best-effort."
  fi

  if [[ -f "${VTC_ROOT}/${probe_script}" ]]; then
    printf '[probe] %s\n' "${env_name}"
    if (
      cd "${VTC_ROOT}/${env_dir}"
      uv run --no-sync python "../../${probe_script}"
    ); then
      probe_status="pass"
    else
      probe_status="fail"
      notes="${notes} probe failed."
    fi
  else
    probe_status="missing_probe"
    notes="${notes} probe script missing."
  fi

  write_record "${env_name}" "${env_dir}" "${sync_status}" "${probe_status}" "${notes:-completed best-effort}"
}

if [[ "${VTC_ALLOW_HEAVY_ENV_SYNC:-0}" != "1" ]]; then
  cat <<'EOF'
Heavy model environment sync is disabled.

Set VTC_ALLOW_HEAVY_ENV_SYNC=1 to allow uv sync for model-specific envs:
  envs/autogaze
  envs/ov-encoder
  envs/llava-ov2
  envs/lmms-eval
  envs/mps-probe

No model weights will be downloaded by this script.
EOF
fi

run_env "autogaze" "envs/autogaze" "scripts/probe_autogaze_env.py"
run_env "ov_encoder" "envs/ov-encoder" "scripts/probe_ov_encoder_env.py"
run_env "llava_ov2" "envs/llava-ov2" "scripts/probe_llava_ov2_env.py"
run_env "lmms_eval" "envs/lmms-eval" "scripts/probe_lmms_eval_env.py"

if [[ "$(uname -s)" == "Darwin" || "${VTC_ALLOW_MPS_PROBE:-0}" == "1" ]]; then
  run_env "mps_probe" "envs/mps-probe" "scripts/probe_mps_env.py"
else
  write_record "mps_probe" "envs/mps-probe" "skipped_platform" "skipped_platform" "MPS probe is optional and skipped on this host."
fi

aggregate_summary
echo "Wrote ${SUMMARY_PATH}"
