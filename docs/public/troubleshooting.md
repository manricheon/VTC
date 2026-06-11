# Troubleshooting

Use these checks from the VTC repository root unless noted.

## uv Missing

Check:

```bash
command -v uv || true
```

Install:

```bash
bash scripts/install_uv_linux.sh
```

## ffmpeg Missing

Check:

```bash
bash scripts/check_system_deps.sh
command -v ffmpeg || true
ffmpeg -version || true
```

Install examples:

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
sudo dnf install -y ffmpeg
brew install ffmpeg
conda install -c conda-forge ffmpeg
```

Codec backend and lmms-eval video work should treat `ffmpeg` as required.

## HF_TOKEN Missing

Public assets may work without a token. Gated or private repos require auth.

Check:

```bash
source scripts/env_weights.sh
cd envs/hf-tools
uv run python ../../scripts/hf_auth_check.py || true
cd ../..
```

Do not paste tokens into files. Use `HF_TOKEN` or HF CLI login state under
`HF_HOME`.

## Weights Missing

Check:

```bash
bash scripts/check_hf_assets.sh
```

Do not download unless explicitly intended. See:

```bash
python scripts/hf_download_plan.py
```

## External Source Missing

Check:

```bash
bash scripts/audit_external_sources.sh
```

External sources live under `external/` and are not committed.

## Heavy Env Sync Failure

Model envs are isolated. Do not install model dependencies into bridge-core.

Run only when ready:

```bash
VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh
```

Inspect:

```bash
bash scripts/run_compat_probes.sh || true
```

## flash_attn Missing

`flash_attn` is not required for bridge-core. It may be required for CUDA model
runtime paths.

Check source status:

```bash
cat docs/public/attention_backend_status.md
```

Do not patch around `flash_attn` until the isolated model env import probe shows
the exact failure.

## CUDA Unavailable

CUDA is not assumed by bridge-core. Real LLaVA-OV2 generation and many
FlashAttention paths should be tested on Linux/CUDA.

## MPS Optional

MPS is a best-effort Mac probe only. It is not official support.

## Profile Files Missing

Run smokes:

```bash
bash scripts/run_all_smokes.sh
```

Summarize:

```bash
bash scripts/run_profile_summaries.sh
```

## Smoke Output Missing

Project A:

```bash
bash scripts/run_project_a_examples.sh
```

Project B:

```bash
bash scripts/run_project_b_examples.sh
```

Smoke outputs are ignored by git under `projects/gaze-ov-bridge/out/`.
