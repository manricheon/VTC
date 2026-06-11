#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# shellcheck disable=SC1091
source "${VTC_ROOT}/scripts/env_weights.sh" >/dev/null

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"
mkdir -p "${UV_CACHE_DIR}" "${VTC_ROOT}/weights/checkpoints"

HF_TOOLS_DIR="${VTC_ROOT}/envs/hf-tools"
SNAPSHOT_SCRIPT="../../scripts/hf_download_snapshot.py"
WEIGHTS_DOC="${VTC_ROOT}/docs/public/weights_snapshot.md"

AUTOGAZE_REPO="nvidia/AutoGaze"
OV_REPO="lmms-lab-encoder/onevision-encoder-large"
LLAVA_REPO="lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct"

AUTOGAZE_DIR="${VTC_ROOT}/weights/checkpoints/AutoGaze"
OV_DIR="${VTC_ROOT}/weights/checkpoints/onevision-encoder-large"
LLAVA_DIR="${VTC_ROOT}/weights/checkpoints/LLaVA-OneVision-2-8B-Instruct"

mkdir -p "${AUTOGAZE_DIR}" "${OV_DIR}" "${LLAVA_DIR}"

status_autogaze="skipped"
status_ov="skipped"
status_llava="skipped"
next_autogaze="Set VTC_ALLOW_WEIGHT_DOWNLOAD=1 and VTC_DOWNLOAD_AUTOGAZE=1, then rerun."
next_ov="Set VTC_ALLOW_WEIGHT_DOWNLOAD=1 and VTC_DOWNLOAD_OV_ENCODER=1, then rerun."
next_llava="Set VTC_ALLOW_WEIGHT_DOWNLOAD=1, VTC_DOWNLOAD_LLAVA_OV2=1, and VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1, then rerun."

token_used() {
  if [[ -n "${HF_TOKEN:-}" ]]; then
    printf 'yes'
  else
    printf 'no'
  fi
}

file_count() {
  local dir="$1"
  if [[ ! -d "${dir}" ]]; then
    printf '0'
    return
  fi
  find "${dir}" -type f | wc -l | tr -d ' '
}

payload_count() {
  local dir="$1"
  if [[ ! -d "${dir}" ]]; then
    printf '0'
    return
  fi
  find "${dir}" -type f \( -name '*.safetensors' -o -name '*.bin' -o -name '*.pt' -o -name '*.pth' -o -name '*.gguf' -o -name '*.onnx' \) | wc -l | tr -d ' '
}

dir_size() {
  local dir="$1"
  if [[ -d "${dir}" ]]; then
    du -sh "${dir}" 2>/dev/null | awk '{print $1}'
  else
    printf 'missing'
  fi
}

manifest_revision() {
  local dir="$1"
  if [[ -f "${dir}/snapshot_manifest.json" ]]; then
    python3 - "$dir/snapshot_manifest.json" <<'PY'
import json
import sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(data.get("revision") or "default")
PY
  else
    printf 'not downloaded'
  fi
}

classify_download_result() {
  local code="$1"
  local dir="$2"
  local payload
  payload="$(payload_count "${dir}")"
  if [[ "${code}" == "0" && "${payload}" != "0" ]]; then
    printf 'downloaded'
  elif [[ "${code}" == "2" ]]; then
    printf 'auth_required'
  elif [[ "${code}" == "5" ]]; then
    printf 'insufficient_disk'
  elif [[ "${code}" == "0" ]]; then
    printf 'failed'
  else
    printf 'failed'
  fi
}

run_hf_tool() {
  (
    cd "${HF_TOOLS_DIR}"
    uv run python "$@"
  )
}

download_snapshot() {
  local repo_id="$1"
  local local_dir="$2"
  set +e
  run_hf_tool "${SNAPSHOT_SCRIPT}" \
    --repo-id "${repo_id}" \
    --repo-type model \
    --local-dir "${local_dir}" \
    --cache-dir "${HF_HUB_CACHE}"
  local code=$?
  set -e
  return "${code}"
}

write_doc() {
  local now disk_root disk_weights token
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  disk_root="$(df -h "${VTC_ROOT}" | awk 'NR==2 {print $4 " available on " $1}')"
  disk_weights="$(df -h "${VTC_ROOT}/weights" | awk 'NR==2 {print $4 " available on " $1}')"
  token="$(token_used)"

  cat > "${WEIGHTS_DOC}" <<EOF
# Hugging Face Weights Snapshot

Snapshot date: \`${now}\`

No model inference was run by the weight setup helper. Downloaded files, if any, remain under \`weights/\` and must not be committed.

## Preflight

Cache policy:

- \`HF_HOME=${HF_HOME}\`
- \`HF_HUB_CACHE=${HF_HUB_CACHE}\`

Authentication:

- \`HF_TOKEN\`: $(if [[ "${token}" == "yes" ]]; then echo "set, value hidden"; else echo "not set"; fi)
- Token used field below records only whether \`HF_TOKEN\` was present; it never contains the token value.

Disk:

- Repository filesystem: ${disk_root}
- \`weights/\` filesystem: ${disk_weights}

Download flags:

- \`VTC_ALLOW_WEIGHT_DOWNLOAD\`: ${VTC_ALLOW_WEIGHT_DOWNLOAD:-not set}
- \`VTC_DOWNLOAD_AUTOGAZE\`: ${VTC_DOWNLOAD_AUTOGAZE:-not set}
- \`VTC_DOWNLOAD_OV_ENCODER\`: ${VTC_DOWNLOAD_OV_ENCODER:-not set}
- \`VTC_DOWNLOAD_LLAVA_OV2\`: ${VTC_DOWNLOAD_LLAVA_OV2:-not set}
- \`VTC_ALLOW_LLAVA_OV2_DOWNLOAD\`: ${VTC_ALLOW_LLAVA_OV2_DOWNLOAD:-not set}

## Snapshot Table

| Target name | Repo id | Local path | Status | Snapshot revision | File count | Payload file count | Approx total size | Date | Token used | Next action |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| AutoGaze | \`${AUTOGAZE_REPO}\` | \`weights/checkpoints/AutoGaze\` | \`${status_autogaze}\` | \`$(manifest_revision "${AUTOGAZE_DIR}")\` | $(file_count "${AUTOGAZE_DIR}") | $(payload_count "${AUTOGAZE_DIR}") | $(dir_size "${AUTOGAZE_DIR}") | \`${now}\` | ${token} | ${next_autogaze} |
| OneVision-Encoder | \`${OV_REPO}\` | \`weights/checkpoints/onevision-encoder-large\` | \`${status_ov}\` | \`$(manifest_revision "${OV_DIR}")\` | $(file_count "${OV_DIR}") | $(payload_count "${OV_DIR}") | $(dir_size "${OV_DIR}") | \`${now}\` | ${token} | ${next_ov} |
| LLaVA-OV2 | \`${LLAVA_REPO}\` | \`weights/checkpoints/LLaVA-OneVision-2-8B-Instruct\` | \`${status_llava}\` | \`$(manifest_revision "${LLAVA_DIR}")\` | $(file_count "${LLAVA_DIR}") | $(payload_count "${LLAVA_DIR}") | $(dir_size "${LLAVA_DIR}") | \`${now}\` | ${token} | ${next_llava} |

## Rerun Commands

AutoGaze:

\`\`\`bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \\
VTC_DOWNLOAD_AUTOGAZE=1 \\
bash scripts/setup_hf_assets.sh
\`\`\`

OneVision-Encoder:

\`\`\`bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \\
VTC_DOWNLOAD_OV_ENCODER=1 \\
bash scripts/setup_hf_assets.sh
\`\`\`

LLaVA-OV2:

\`\`\`bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \\
VTC_DOWNLOAD_LLAVA_OV2=1 \\
VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 \\
bash scripts/setup_hf_assets.sh
\`\`\`

All selected public-visible targets in one pass:

\`\`\`bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \\
VTC_DOWNLOAD_AUTOGAZE=1 \\
VTC_DOWNLOAD_OV_ENCODER=1 \\
VTC_DOWNLOAD_LLAVA_OV2=1 \\
VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 \\
bash scripts/setup_hf_assets.sh
\`\`\`

## Current Readiness

Ready for environment compatibility probes:

- bridge-core remains ready.
- model-env import probes that do not require weights can proceed.

Weight-backed model probes can proceed only for rows marked \`downloaded\`, and only after the matching isolated model env is synced/probed:

- AutoGaze requires payload files under \`weights/checkpoints/AutoGaze\`.
- OneVision-Encoder requires payload files under \`weights/checkpoints/onevision-encoder-large\`.
- LLaVA-OV2 requires payload files under \`weights/checkpoints/LLaVA-OneVision-2-8B-Instruct\`.

EOF
}

if [[ "${VTC_ALLOW_WEIGHT_DOWNLOAD:-0}" != "1" ]]; then
  echo "Weight downloads are disabled because VTC_ALLOW_WEIGHT_DOWNLOAD is not 1."
  write_doc
  exit 0
fi

if [[ "${VTC_DOWNLOAD_AUTOGAZE:-0}" != "1" && "${VTC_DOWNLOAD_OV_ENCODER:-0}" != "1" && "${VTC_DOWNLOAD_LLAVA_OV2:-0}" != "1" ]]; then
  echo "Weight downloads are enabled, but no target flag is set."
  write_doc
  exit 0
fi

(
  cd "${HF_TOOLS_DIR}"
  uv sync
)

run_hf_tool "../../scripts/hf_auth_check.py" --public-only-ok || true

failures=0

if [[ "${VTC_DOWNLOAD_AUTOGAZE:-0}" == "1" ]]; then
  echo "Downloading AutoGaze weights from verified repo: ${AUTOGAZE_REPO}"
  if download_snapshot "${AUTOGAZE_REPO}" "${AUTOGAZE_DIR}"; then
    status_autogaze="$(classify_download_result 0 "${AUTOGAZE_DIR}")"
    next_autogaze="No action if payload files are present; otherwise inspect download output and rerun."
  else
    code=$?
    status_autogaze="$(classify_download_result "${code}" "${AUTOGAZE_DIR}")"
    next_autogaze="Authenticate if needed, then rerun with VTC_ALLOW_WEIGHT_DOWNLOAD=1 VTC_DOWNLOAD_AUTOGAZE=1 bash scripts/setup_hf_assets.sh."
    failures=$((failures + 1))
  fi
fi

if [[ "${VTC_DOWNLOAD_OV_ENCODER:-0}" == "1" ]]; then
  echo "Downloading OneVision-Encoder weights"
  if download_snapshot "${OV_REPO}" "${OV_DIR}"; then
    status_ov="$(classify_download_result 0 "${OV_DIR}")"
    next_ov="No action if payload files are present; otherwise inspect download output and rerun."
  else
    code=$?
    status_ov="$(classify_download_result "${code}" "${OV_DIR}")"
    next_ov="Authenticate if needed, then rerun with VTC_ALLOW_WEIGHT_DOWNLOAD=1 VTC_DOWNLOAD_OV_ENCODER=1 bash scripts/setup_hf_assets.sh."
    failures=$((failures + 1))
  fi
fi

if [[ "${VTC_DOWNLOAD_LLAVA_OV2:-0}" == "1" ]]; then
  if [[ "${VTC_ALLOW_LLAVA_OV2_DOWNLOAD:-0}" != "1" ]]; then
    echo "Skipping LLaVA-OV2 because VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 is required."
    status_llava="skipped"
    next_llava="Set VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1, then rerun."
  else
    echo "Downloading LLaVA-OV2 weights"
    if download_snapshot "${LLAVA_REPO}" "${LLAVA_DIR}"; then
      status_llava="$(classify_download_result 0 "${LLAVA_DIR}")"
      next_llava="No action if payload files are present; otherwise inspect download output and rerun."
    else
      code=$?
      status_llava="$(classify_download_result "${code}" "${LLAVA_DIR}")"
      next_llava="Authenticate if needed, then rerun with VTC_ALLOW_WEIGHT_DOWNLOAD=1 VTC_DOWNLOAD_LLAVA_OV2=1 VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 bash scripts/setup_hf_assets.sh."
      failures=$((failures + 1))
    fi
  fi
fi

write_doc
echo "Updated ${WEIGHTS_DOC}"
exit "${failures}"
