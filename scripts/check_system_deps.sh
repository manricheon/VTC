#!/usr/bin/env bash
set -euo pipefail

missing=()

check_cmd() {
  local name="$1"
  local version_cmd="${2:-}"
  local path

  if path="$(command -v "${name}" 2>/dev/null)"; then
    echo "[ok] ${name}: ${path}"
    if [[ -n "${version_cmd}" ]]; then
      # Version commands are diagnostic only; a failing version print should not
      # make the dependency look missing when the executable exists.
      bash -c "${version_cmd}" 2>/dev/null | head -n 1 || true
    fi
  else
    echo "[missing] ${name}"
    missing+=("${name}")
  fi
}

echo "System dependency check"
echo "platform: $(uname -a)"
if [[ -f /etc/os-release ]]; then
  echo "os-release:"
  sed -n '1,8p' /etc/os-release
else
  echo "os-release: not available"
fi
echo

check_cmd "git" "git --version"
check_cmd "curl" "curl --version"
check_cmd "ffmpeg" "ffmpeg -version"

echo
if (( ${#missing[@]} == 0 )); then
  echo "All checked system dependencies are available."
  exit 0
fi

echo "Missing system dependencies: ${missing[*]}"
echo "Install ffmpeg on the Linux target before running codec backend tests."
echo "Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y ffmpeg"
echo "RHEL/CentOS/Fedora: sudo dnf install -y ffmpeg"
echo "Conda: conda install -c conda-forge ffmpeg"

if [[ "${REQUIRED_SYSTEM_DEPS:-0}" == "1" ]]; then
  exit 1
fi

exit 0
