# Hugging Face Access Status

Status date: `2026-06-11T13:12:23Z`

HF tokens must never be printed, logged, or committed. This status records only whether a token was present.

## Current Access Mode

Current shell:

- `HF_TOKEN`: not set
- Mode: public-only

Cache policy after `source scripts/env_weights.sh`:

- `HF_HOME=/Users/mrc/Documents/VTC/weights/hf_home`
- `HF_HUB_CACHE=/Users/mrc/Documents/VTC/weights/hf_home/hub`

## Repo Access Status

| Repo | Purpose | Current status |
| --- | --- | --- |
| `nvidia/AutoGaze` | AutoGaze weights | payload present under `weights/checkpoints/AutoGaze` |
| `lmms-lab-encoder/onevision-encoder-large` | OneVision-Encoder weights/code | payload present under `weights/checkpoints/onevision-encoder-large` |
| `lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct` | LLaVA-OV2 weights/code | payload present under `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct` |
| `bfshi/AutoGaze` | stale/ambiguous AutoGaze reference | not selected |

No active gated failure was hit in this pass. A token may still be useful for rate limits or future private/gated repos.

## Safe Auth Commands

Environment-token mode:

```bash
source scripts/env_weights.sh
export HF_TOKEN=<token from Hugging Face settings>
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

If a future download reports gated/private access, request access for that exact repo, authenticate safely, then rerun only the needed target.
