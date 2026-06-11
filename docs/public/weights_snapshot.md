# Hugging Face Weights Snapshot

Snapshot date: `2026-06-11T07:41:51Z`

No model inference was run by the weight setup helper. Downloaded files, if any, remain under `weights/` and must not be committed.

## Preflight

Cache policy:

- `HF_HOME=/Users/mrc/Documents/VTC/weights/hf_home`
- `HF_HUB_CACHE=/Users/mrc/Documents/VTC/weights/hf_home/hub`

Authentication:

- `HF_TOKEN`: not set
- Token used field below records only whether `HF_TOKEN` was present; it never contains the token value.

Disk:

- Repository filesystem: 23Gi available on /dev/disk3s5
- `weights/` filesystem: 23Gi available on /dev/disk3s5

Download flags:

- `VTC_ALLOW_WEIGHT_DOWNLOAD`: 1
- `VTC_DOWNLOAD_AUTOGAZE`: 1
- `VTC_DOWNLOAD_OV_ENCODER`: 1
- `VTC_DOWNLOAD_LLAVA_OV2`: 1
- `VTC_ALLOW_LLAVA_OV2_DOWNLOAD`: 1

## Snapshot Table

| Target name | Repo id | Local path | Status | Snapshot revision | File count | Payload file count | Approx total size | Date | Token used | Next action |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| AutoGaze | `nvidia/AutoGaze` | `weights/checkpoints/AutoGaze` | `downloaded` | `default` | 15 | 1 | 13M | `2026-06-11T07:41:51Z` | no | No action if payload files are present; otherwise inspect download output and rerun. |
| OneVision-Encoder | `lmms-lab-encoder/onevision-encoder-large` | `weights/checkpoints/onevision-encoder-large` | `downloaded` | `default` | 19 | 1 | 602M | `2026-06-11T07:41:51Z` | no | No action if payload files are present; otherwise inspect download output and rerun. |
| LLaVA-OV2 | `lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct` | `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct` | `downloaded` | `default` | 51 | 4 | 16G | `2026-06-11T07:41:51Z` | no | No action if payload files are present; otherwise inspect download output and rerun. |

## Rerun Commands

AutoGaze:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_AUTOGAZE=1 \
bash scripts/setup_hf_assets.sh
```

OneVision-Encoder:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_OV_ENCODER=1 \
bash scripts/setup_hf_assets.sh
```

LLaVA-OV2:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_LLAVA_OV2=1 \
VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 \
bash scripts/setup_hf_assets.sh
```

All selected public-visible targets in one pass:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_AUTOGAZE=1 \
VTC_DOWNLOAD_OV_ENCODER=1 \
VTC_DOWNLOAD_LLAVA_OV2=1 \
VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 \
bash scripts/setup_hf_assets.sh
```

## Current Readiness

Ready for environment compatibility probes:

- bridge-core remains ready.
- model-env import probes that do not require weights can proceed.

Weight-backed model probes can proceed only for rows marked `downloaded`, and only after the matching isolated model env is synced/probed:

- AutoGaze requires payload files under `weights/checkpoints/AutoGaze`.
- OneVision-Encoder requires payload files under `weights/checkpoints/onevision-encoder-large`.
- LLaVA-OV2 requires payload files under `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct`.
