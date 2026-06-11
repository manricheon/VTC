# System Dependencies

Check date: `2026-06-11T06:10:32Z`

VTC remains Linux-first. The current check was run on the local development host and does not replace verification on the official Linux target.

## Current Host

Command:

```bash
uname -a
cat /etc/os-release || true
```

Result:

- `uname -a`: `Darwin mrcui-MacBookAir.local 25.4.0 Darwin Kernel Version 25.4.0: Thu Mar 19 19:32:36 PDT 2026; root:xnu-12377.101.15~1/RELEASE_ARM64_T8103 arm64`
- `/etc/os-release`: not available on this host

Official target status:

- Linux remains the official target.
- Linux `ffmpeg` status is not verified until these checks are run on the Linux machine.

## ffmpeg Status

Commands run:

```bash
command -v ffmpeg || true
ffmpeg -version || true
```

Result:

- `command -v ffmpeg`: no path found
- `ffmpeg -version`: `command not found`
- Detected ffmpeg path: not available
- Detected ffmpeg version: not available
- Installation status: not installed by this task
- `ALLOW_SYSTEM_INSTALL`: not set

Classification:

- `ffmpeg` is unresolved for codec/backend tests on the current host.
- Linux target status remains not verified.
- The LLaVA-OV2 codec workflow remains blocked until `ffmpeg` is installed and verified on the target runtime.

## System Dependency Checker

Use:

```bash
bash scripts/check_system_deps.sh
```

The checker reports:

- `git`
- `curl`
- `ffmpeg`

It does not install anything.

By default it exits 0 after reporting missing dependencies. To make missing dependencies fail CI or a setup gate:

```bash
REQUIRED_SYSTEM_DEPS=1 bash scripts/check_system_deps.sh
```

## Why ffmpeg Matters

The LLaVA-OV2 HF custom-code codec module `codec_video_processing_llava_onevision2.py` documents that codec preprocessing invokes `codec-video-prep` / `cv-preinfer` and requires `ffmpeg` on `PATH`.

Level 1 bridge-core tests do not require `ffmpeg`.

Expected `ffmpeg` requirement:

- Not required for pure Python Project A/B synthetic tests.
- Required for LLaVA-OV2 codec backend video preprocessing.
- Likely required for later real video decode and benchmark workflows.

## Manual Install Commands

Do not run these automatically unless a task explicitly allows system installation.

Ubuntu/Debian:

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

RHEL/CentOS/Fedora:

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
