#!/usr/bin/env bash
set -euo pipefail

missing=()
optional_missing=()

is_macos() {
  [[ "$(uname -s)" == "Darwin" ]]
}

is_linux() {
  [[ "$(uname -s)" == "Linux" ]]
}

check_cmd() {
  local name="$1"
  local version_cmd="${2:-}"
  local required="${3:-1}"
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
    if [[ "${required}" == "1" ]]; then
      missing+=("${name}")
    else
      optional_missing+=("${name}")
    fi
  fi
}

print_install_commands() {
  cat <<'EOF'
Install commands for ffmpeg:
  macOS Homebrew: brew install ffmpeg
  Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y ffmpeg
  Fedora/RHEL: sudo dnf install -y ffmpeg
  Conda: conda install -c conda-forge ffmpeg
EOF
}

attempt_ffmpeg_install() {
  if command -v ffmpeg >/dev/null 2>&1; then
    return 0
  fi
  if [[ "${ALLOW_SYSTEM_INSTALL:-0}" != "1" ]]; then
    return 0
  fi

  echo
  echo "ALLOW_SYSTEM_INSTALL=1 is set; attempting ffmpeg install for supported OS."
  if is_macos; then
    if command -v brew >/dev/null 2>&1; then
      brew install ffmpeg
    else
      echo "Homebrew is not installed. Install Homebrew first, then run: brew install ffmpeg"
      return 0
    fi
  elif is_linux; then
    if command -v apt-get >/dev/null 2>&1; then
      sudo apt-get update
      sudo apt-get install -y ffmpeg
    elif command -v dnf >/dev/null 2>&1; then
      sudo dnf install -y ffmpeg
    elif command -v yum >/dev/null 2>&1; then
      sudo yum install -y ffmpeg
    elif command -v pacman >/dev/null 2>&1; then
      sudo pacman -Sy --noconfirm ffmpeg
    else
      echo "No supported package manager found for automatic ffmpeg install."
      print_install_commands
    fi
  else
    echo "Unsupported OS for automatic ffmpeg install: $(uname -s)"
    print_install_commands
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

attempt_ffmpeg_install

check_cmd "bash" "bash --version" "1"
check_cmd "git" "git --version" "1"
check_cmd "curl" "curl --version" "1"
check_cmd "uv" "uv --version" "1"
check_cmd "python" "python --version" "0"
check_cmd "python3" "python3 --version" "0"
check_cmd "ffmpeg" "ffmpeg -version" "1"

echo
if (( ${#optional_missing[@]} > 0 )); then
  echo "Optional or local-diagnostic commands missing: ${optional_missing[*]}"
fi

if (( ${#missing[@]} == 0 )); then
  echo "All required checked system dependencies are available."
  exit 0
fi

echo "Missing required system dependencies: ${missing[*]}"
if [[ " ${missing[*]} " == *" ffmpeg "* ]]; then
  echo "Install ffmpeg on the Linux target before running codec backend tests."
  print_install_commands
fi

if [[ "${REQUIRED_SYSTEM_DEPS:-0}" == "1" ]]; then
  exit 1
fi

exit 0
