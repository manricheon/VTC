# System Dependencies

Check date: `2026-06-11T06:01:56Z`

VTC remains Linux-first. The current check was run on the local development host and does not replace verification on the official Linux target.

## ffmpeg Status

Commands run:

```bash
command -v ffmpeg || true
ffmpeg -version || true
```

Result:

- `command -v ffmpeg`: no path found
- `ffmpeg -version`: `command not found`
- Detected ffmpeg version: not available
- Install attempted: no

Classification:

- `ffmpeg` is currently a system dependency blocker for codec/backend tests on this host.
- Linux target status is still not verified until the same commands are run on the Linux machine.

## Why ffmpeg Matters

The LLaVA-OV2 HF custom-code codec module `codec_video_processing_llava_onevision2.py` documents that codec preprocessing invokes `codec-video-prep` / `cv-preinfer` and requires `ffmpeg` on `PATH`.

Level 1 bridge-core tests do not require `ffmpeg`.

Expected `ffmpeg` requirement:

- Not required for pure Python Project A/B synthetic tests.
- Required for LLaVA-OV2 codec backend video preprocessing.
- Likely required for later real video decode and benchmark workflows.

## Install Commands

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
```

Record the output before running codec/backend smoke tests.
