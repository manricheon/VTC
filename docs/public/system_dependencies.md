# System Dependencies

Check date: `2026-06-11T07:28:02Z`

VTC remains Linux-first. The current check was run on the local macOS development host and does not replace verification on the official Linux target.

## Current Host

Commands:

```bash
uname -a
if [ -f /etc/os-release ]; then cat /etc/os-release; fi
sw_vers 2>/dev/null || true
command -v ffmpeg || true
ffmpeg -version || true
```

Result:

- Platform: `Darwin mrcui-MacBookAir.local 25.4.0 ... arm64`
- macOS: `26.4.1`
- `/etc/os-release`: not available on this host
- `ffmpeg`: not found on `PATH`
- `ALLOW_SYSTEM_INSTALL`: not set, so no install was attempted

Official target status:

- Linux remains the official target.
- Linux `ffmpeg` status is not verified until these checks are run on the Linux machine.

## ffmpeg Status

Status: `missing_or_unverified`

Detected path: not available.

Detected version: not available.

Installation status: not installed by this task.

Codec/backend impact:

- Project A and Project B pure-Python synthetic tests do not require `ffmpeg`.
- LLaVA-OV2 codec/backend preprocessing remains blocked until `ffmpeg` is installed and verified.
- Later real video decode and `lmms-eval` video workflows should treat `ffmpeg` as required.

## System Dependency Checker

Use:

```bash
bash scripts/check_system_deps.sh
```

The checker reports:

- `bash`
- `git`
- `curl`
- `uv`
- `python`
- `python3`
- `ffmpeg`

By default it exits 0 after reporting missing dependencies. To make missing required dependencies fail a setup gate:

```bash
REQUIRED_SYSTEM_DEPS=1 bash scripts/check_system_deps.sh
```

If `ALLOW_SYSTEM_INSTALL=1` is set, the checker may attempt an `ffmpeg` install through a supported system package manager. It does not use `sudo` unless `ALLOW_SYSTEM_INSTALL=1` is set.

## Manual Install Commands

Do not run these automatically unless a task explicitly allows system installation.

macOS Homebrew:

```bash
brew install ffmpeg
```

Ubuntu/Debian:

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

Fedora/RHEL:

```bash
sudo dnf install -y ffmpeg
```

Conda alternative:

```bash
conda install -c conda-forge ffmpeg
```

## Verification Command

After installation on the Linux target:

```bash
command -v ffmpeg
ffmpeg -version
bash scripts/check_system_deps.sh
```

Record the path and version before running codec/backend smoke tests.
