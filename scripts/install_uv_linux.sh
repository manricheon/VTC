#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
    uv --version
    exit 0
fi

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "uv is not installed. This installer is intended for Linux targets." >&2
    echo "Install uv manually for this platform or run on Linux." >&2
    exit 1
fi

curl -LsSf https://astral.sh/uv/install.sh | sh

if command -v uv >/dev/null 2>&1; then
    uv --version
else
    echo "uv was installed, but it is not available on PATH in this shell." >&2
    echo "Open a new shell or add the uv install directory to PATH, then rerun this script." >&2
fi
