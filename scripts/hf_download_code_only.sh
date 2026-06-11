#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

source "${VTC_ROOT}/scripts/env_weights.sh"

mkdir -p "${VTC_ROOT}/external"

(
  cd "${VTC_ROOT}/envs/hf-tools"
  uv run python ../../scripts/hf_download_snapshot.py \
    --repo-id "lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct" \
    --repo-type model \
    --local-dir "${VTC_ROOT}/external/LLaVA-OneVision-2-8B-Instruct-code" \
    --cache-dir "${HF_HUB_CACHE}" \
    --allow-pattern "*.py" \
    --allow-pattern "*.json" \
    --allow-pattern "*.md" \
    --allow-pattern "*.txt" \
    --allow-pattern "tokenizer*" \
    --allow-pattern "preprocessor*" \
    --allow-pattern "processor*" \
    --allow-pattern "generation_config.json" \
    --allow-pattern "config.json" \
    --ignore-pattern "*.safetensors" \
    --ignore-pattern "*.bin" \
    --ignore-pattern "*.pt" \
    --ignore-pattern "*.pth" \
    --ignore-pattern "*.gguf" \
    --ignore-pattern "*.onnx"
)

