# Hugging Face Downloads

VTC keeps Hugging Face tooling isolated from bridge-core and model-specific environments. The `envs/hf-tools` environment contains only `huggingface-hub` and lightweight utility dependencies. It does not install `torch`, `transformers`, AutoGaze, OneVision-Encoder, LLaVA-OV2, or `lmms-eval`.

Do not commit tokens, downloaded weights, Hugging Face caches, or external source snapshots.

## Cache Policy

All Hugging Face cache material must stay under `weights/`.

From the VTC root:

```bash
source scripts/env_weights.sh
```

This sets:

- `HF_HOME=<VTC_ROOT>/weights/hf_home`
- `HF_HUB_CACHE=<VTC_ROOT>/weights/hf_home/hub`

`weights/` is gitignored. Downloaded model weights belong under:

- `weights/checkpoints/AutoGaze`
- `weights/checkpoints/onevision-encoder-large`
- `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct`

## Token-Safe Authentication

Tokens may be supplied only through:

- `HF_TOKEN` environment variable
- Hugging Face CLI login state under `HF_HOME`
- an interactive shell prompt that does not echo the token

Do not paste tokens into project files.

Setup and check auth:

```bash
source scripts/env_weights.sh
cd envs/hf-tools
uv sync
uv run python ../../scripts/hf_auth_check.py
cd ../..
```

If unauthenticated, either export a token for the current shell:

```bash
export HF_TOKEN=<token from https://huggingface.co/settings/tokens>
```

or use the Hugging Face CLI if installed:

```bash
source scripts/env_weights.sh
cd envs/hf-tools
uv run hf auth login
```

The auth checker prints whether a token is present, but never prints token values.

## Public-Only Mode

Some repo metadata or public code snapshots may work without a token. For public-only diagnostics:

```bash
source scripts/env_weights.sh
cd envs/hf-tools
uv run python ../../scripts/hf_auth_check.py --public-only-ok
```

Public-only mode is not enough for gated/private weights.

## Gated Repo Handling

If a repo is gated or private, the snapshot wrapper stops and prints:

- which repo failed
- whether authentication or access approval is likely required
- how to authenticate and rerun

Do not work around gated access by moving caches outside `weights/`.

## Download Plan

Print the intended downloads without downloading files:

```bash
source scripts/env_weights.sh
cd envs/hf-tools
uv run python ../../scripts/hf_download_plan.py
cd ../..
```

Candidate repos:

- AutoGaze candidates:
  - `nvidia/AutoGaze`
  - `bfshi/AutoGaze`
- OneVision-Encoder:
  - `lmms-lab-encoder/onevision-encoder-large`
- LLaVA-OV2:
  - `lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct`

AutoGaze repo choice must be verified from `external/AutoGaze` docs or HF repo files before use.

## Code-Only Snapshot

The code-only LLaVA-OV2 custom-code snapshot goes under `external/`, not `weights/`:

```bash
source scripts/env_weights.sh
bash scripts/hf_download_code_only.sh
```

The code-only script includes code/config/text files and excludes model payload files such as `.safetensors`, `.bin`, `.pt`, `.pth`, `.gguf`, and `.onnx`.

`external/` is gitignored.

## Weight Downloads

Weight downloads require an explicit allow flag and a specific target flag.

Download OneVision-Encoder:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 VTC_DOWNLOAD_OV_ENCODER=1 bash scripts/hf_download_weights.sh
```

Download LLaVA-OV2:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 VTC_DOWNLOAD_LLAVA_OV2=1 bash scripts/hf_download_weights.sh
```

Download AutoGaze after verifying the correct repo:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 VTC_DOWNLOAD_AUTOGAZE=1 VTC_AUTOGAZE_REPO=<repo-id> bash scripts/hf_download_weights.sh
```

If no target flag is selected, the script prints the plan and exits. If `VTC_ALLOW_WEIGHT_DOWNLOAD=1` is absent, the script refuses to download.

## Git Policy

- `weights/` is gitignored.
- `external/` is gitignored.
- `artifacts/` is gitignored.
- Download manifests under ignored download directories are runtime evidence and should not be committed.
