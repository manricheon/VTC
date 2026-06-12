#!/usr/bin/env bash
set -euo pipefail

VTC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OS_NAME="$(uname -s)"

if [[ "${OS_NAME}" != "Linux" ]]; then
    echo "Warning: bridge-core is officially targeted at Linux; detected ${OS_NAME}." >&2
    if [[ "${ALLOW_NON_LINUX:-0}" != "1" ]]; then
        echo "Set ALLOW_NON_LINUX=1 to run this best-effort local probe." >&2
        exit 1
    fi
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required. Run: bash scripts/install_uv_linux.sh" >&2
    exit 1
fi

cd "${VTC_ROOT}/envs/bridge-core"

uv sync --group dev
uv run python -m compileall ../../projects/gaze-ov-bridge/src
uv run python -m compileall ../../projects/projector-eval-harness/src
pytest_status=0
uv run pytest -q ../../projects/gaze-ov-bridge/tests || pytest_status=$?
if [[ "${pytest_status}" -eq 5 ]]; then
    echo "No tests collected yet; bridge-core bootstrap continues for the skeleton."
elif [[ "${pytest_status}" -ne 0 ]]; then
    exit "${pytest_status}"
fi
uv run pytest -q ../../projects/projector-eval-harness/tests
