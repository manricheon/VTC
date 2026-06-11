# Hugging Face Weights Snapshot

Snapshot date: `2026-06-11T06:15:22Z`

No model inference was run. No weights were downloaded in this pass because `VTC_ALLOW_WEIGHT_DOWNLOAD` was not set to `1`.

## Preflight

Cache policy:

- `HF_HOME=/Users/mrc/Documents/VTC/weights/hf_home`
- `HF_HUB_CACHE=/Users/mrc/Documents/VTC/weights/hf_home/hub`

Authentication:

- `HF_TOKEN`: not set
- Hugging Face CLI login under `HF_HOME`: not authenticated
- Public-only metadata/code access is available; private or gated repos still require user authentication.

Disk:

- Repository filesystem: 460 GiB total, 397 GiB used, 40 GiB available.
- `weights/` filesystem: same mount, 40 GiB available.
- No disk blocker was observed for the preflight itself, but disk must be rechecked before large downloads.

Download flags:

- `VTC_ALLOW_WEIGHT_DOWNLOAD`: not set
- `VTC_DOWNLOAD_AUTOGAZE`: not set
- `VTC_DOWNLOAD_OV_ENCODER`: not set
- `VTC_DOWNLOAD_LLAVA_OV2`: not set
- `VTC_ALLOW_LLAVA_OV2_DOWNLOAD`: not set

Checkpoint directories:

- `weights/checkpoints/AutoGaze`: exists, `0B`
- `weights/checkpoints/onevision-encoder-large`: exists, `0B`
- `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct`: exists, `0B`

## Snapshot Table

| Target name | Repo id | Local path | Status | Snapshot revision | File count | Approx total size | Date | Token used | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AutoGaze | `nvidia/AutoGaze` | `weights/checkpoints/AutoGaze` | `skipped` | not downloaded | 0 | 0B local | `2026-06-11T06:15:22Z` | no | Set `VTC_ALLOW_WEIGHT_DOWNLOAD=1` and `VTC_DOWNLOAD_AUTOGAZE=1`, then rerun. |
| OneVision-Encoder | `lmms-lab-encoder/onevision-encoder-large` | `weights/checkpoints/onevision-encoder-large` | `skipped` | not downloaded | 0 | 0B local | `2026-06-11T06:15:22Z` | no | Set `VTC_ALLOW_WEIGHT_DOWNLOAD=1` and `VTC_DOWNLOAD_OV_ENCODER=1`, then rerun. |
| LLaVA-OV2 | `lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct` | `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct` | `skipped` | not downloaded | 0 | 0B local | `2026-06-11T06:15:22Z` | no | Set `VTC_ALLOW_WEIGHT_DOWNLOAD=1`, `VTC_DOWNLOAD_LLAVA_OV2=1`, and `VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1`, then rerun. |

## Rerun Commands

AutoGaze:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_AUTOGAZE=1 \
VTC_AUTOGAZE_REPO=nvidia/AutoGaze \
bash scripts/hf_download_weights.sh
```

OneVision-Encoder:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_OV_ENCODER=1 \
bash scripts/hf_download_weights.sh
```

LLaVA-OV2:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_LLAVA_OV2=1 \
VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 \
bash scripts/hf_download_weights.sh
```

All three public-visible targets in one pass:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_AUTOGAZE=1 \
VTC_AUTOGAZE_REPO=nvidia/AutoGaze \
VTC_DOWNLOAD_OV_ENCODER=1 \
VTC_DOWNLOAD_LLAVA_OV2=1 \
VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 \
bash scripts/hf_download_weights.sh
```

## Auth and Gating Notes

No gated or authentication blocker was encountered during this pass because downloads were skipped before contacting the Hub for payload files.

If a future run fails with gated or private access:

1. Request/accept access for the specific repo on Hugging Face.
2. Authenticate without committing tokens:

```bash
source scripts/env_weights.sh
cd envs/hf-tools
uv run hf auth login
cd ../..
```

or export `HF_TOKEN` only in the current shell:

```bash
export HF_TOKEN=<token>
```

Never paste tokens into project files.

## Current Readiness

Ready for environment compatibility probes:

- bridge-core remains ready.
- model-env import probes that do not require weights can proceed.

Not ready for weight-backed model probes:

- AutoGaze weights are absent.
- OneVision-Encoder weights are absent.
- LLaVA-OV2 weights are absent.

Also unresolved before codec/generation:

- Linux `ffmpeg` is still missing or not verified.
- CUDA/attention-backend compatibility is still unverified.
