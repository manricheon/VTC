# Hugging Face Access Status

Status date: `2026-06-11T07:28:02Z`

HF tokens are never printed or committed. This status records only token presence and public/authenticated mode.

## Cache Policy

After sourcing `scripts/env_weights.sh`:

- `HF_HOME=/Users/mrc/Documents/VTC/weights/hf_home`
- `HF_HUB_CACHE=/Users/mrc/Documents/VTC/weights/hf_home/hub`

All Hugging Face cache material and checkpoint downloads must stay under `weights/`.

## Current Access Mode

Current shell:

- `HF_TOKEN`: not set
- Mode: public-only

Implications:

- Public metadata, code snapshots, and the three requested public-visible weight snapshots worked without a token in this pass.
- Large downloads may hit rate limits without a token.
- Gated or private repos require authentication and possibly access approval.

## Known Repo Access Status

| Repo | Purpose | Current status |
| --- | --- | --- |
| `nvidia/AutoGaze` | AutoGaze weights | downloaded in public-only mode |
| `lmms-lab-encoder/onevision-encoder-large` | OneVision-Encoder weights/code | downloaded in public-only mode |
| `lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct` | LLaVA-OV2 weights/code | downloaded in public-only mode |
| `bfshi/AutoGaze` | stale/ambiguous AutoGaze reference | unavailable in public-only mode; not selected |

No active gated failure was hit in this pass. Downloads ran unauthenticated and produced local payload files under `weights/`.

## Safe Auth Commands

Environment-token mode:

```bash
source scripts/env_weights.sh
export HF_TOKEN=<token from https://huggingface.co/settings/tokens>
cd envs/hf-tools
uv run python ../../scripts/hf_auth_check.py
cd ../..
```

CLI login mode:

```bash
source scripts/env_weights.sh
cd envs/hf-tools
uv run hf auth login
uv run python ../../scripts/hf_auth_check.py
cd ../..
```

Public-only check:

```bash
source scripts/env_weights.sh
cd envs/hf-tools
uv run python ../../scripts/hf_auth_check.py --public-only-ok
cd ../..
```

## Rerun After Access Failure

If a future download reports gated or private access:

1. Request or accept access for the exact repo on Hugging Face.
2. Authenticate using one of the safe modes above.
3. Rerun only the needed target, for example:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_LLAVA_OV2=1 \
VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 \
bash scripts/setup_hf_assets.sh
```
