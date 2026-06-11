# System Dependencies

Check date: `2026-06-11T13:12:23Z`

Official target: Linux + uv. This check was run on the local macOS/MPS-capable development host and must be repeated on the Linux target before codec/backend runtime work.

## Current Host Result

Command:

```bash
bash scripts/check_system_deps.sh
```

Result:

| Dependency | Status | Evidence |
| --- | --- | --- |
| `bash` | available | `/bin/bash` |
| `git` | available | `/usr/bin/git` |
| `curl` | available | `/usr/bin/curl` |
| `uv` | available | `/Users/mrc/.local/bin/uv` |
| `python` | missing | not on PATH |
| `python3` | available | `/usr/bin/python3`, Python 3.9.6 |
| `ffmpeg` | missing | not on PATH |

`python` missing on the host PATH does not block uv-managed bridge-core, because `envs/bridge-core` uses Python 3.11 through uv.

## ffmpeg Status

Status: `missing_or_unverified`

Detected path: not available.

Detected version: not available.

Install action: no install was attempted because `ALLOW_SYSTEM_INSTALL=1` was not set.

Codec/backend impact:

- Project A/B pure-Python tests and synthetic smokes are not blocked.
- LLaVA-OV2 codec/backend runtime tests remain blocked until `ffmpeg` is installed and verified.
- `lmms-eval` video workflows should also treat `ffmpeg` as required.

## Manual Install Commands

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

Conda:

```bash
conda install -c conda-forge ffmpeg
```

## Verification

Run on the official Linux target:

```bash
command -v ffmpeg
ffmpeg -version
bash scripts/check_system_deps.sh
```

Use strict mode only when a setup gate should fail on missing system dependencies:

```bash
REQUIRED_SYSTEM_DEPS=1 bash scripts/check_system_deps.sh
```
