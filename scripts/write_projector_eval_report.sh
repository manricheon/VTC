#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VTC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/vtc-uv-cache}"
export PYTHONPATH="${VTC_ROOT}/projects/projector-eval-harness/src:${PYTHONPATH:-}"

uv run --project "${VTC_ROOT}/envs/bridge-core" \
  python -m vtc_projector_eval.reports --repo-root "${VTC_ROOT}" "$@"
