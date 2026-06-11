# Model Environment Status

Status date: `2026-06-11T07:28:02Z`

No heavy model environment sync was run for this status update because `VTC_ALLOW_HEAVY_ENV_SYNC` is not set to `1`. Model weights are now present under `weights/checkpoints/`, but no model inference was run.

## Policy

Each model family remains isolated:

- `envs/autogaze`
- `envs/ov-encoder`
- `envs/llava-ov2`
- `envs/lmms-eval`
- `envs/mps-probe`

Do not merge these dependencies into `envs/bridge-core`.

## Current Summary

| Env | uv sync status | Import probe status | Current blocker | Next command |
| --- | --- | --- | --- | --- |
| `envs/autogaze` | skipped by policy | partial from previous no-sync probe | heavy deps and FlashAttention policy unresolved | `VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh` |
| `envs/ov-encoder` | skipped by policy | partial from previous no-sync probe | `torch`/`transformers` absent, fallback unverified | `VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh` |
| `envs/llava-ov2` | skipped by policy | partial from previous no-sync probe | runtime deps and `ffmpeg` absent/unverified | `VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh` |
| `envs/lmms-eval` | skipped by policy | partial from previous no-sync probe | benchmark deps and model runtimes absent | Defer until LLaVA-OV2 runtime path works. |
| `envs/mps-probe` | skipped by policy | optional partial probe | optional Mac/MPS diagnostics only; torch absent | `VTC_ALLOW_HEAVY_ENV_SYNC=1 VTC_ALLOW_MPS_PROBE=1 bash scripts/setup_model_envs_best_effort.sh` |

## Best-Effort Wrapper

Use:

```bash
bash scripts/setup_model_envs_best_effort.sh
```

Default behavior:

- Does not run `uv sync`.
- Does not install heavy dependencies.
- Does not download model weights.
- Writes `artifacts/compat/model_envs_best_effort.json` with skipped-by-policy records.

Heavy sync behavior:

```bash
VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh
```

This attempts `uv sync` separately inside each model env and then runs the matching probe script. It continues best-effort if one env fails.

## Readiness Decision

Ready:

- `envs/bridge-core` is ready for Project A/B pure-Python artifact work.

Not ready:

- `envs/autogaze` is not ready for real AutoGaze generation.
- `envs/ov-encoder` is not ready for real OV-Encoder forward.
- `envs/llava-ov2` is not ready for real LLaVA-OV2 generation.
- `envs/lmms-eval` is not ready for full benchmark runs.
- `envs/mps-probe` is optional and not an official compatibility gate.

Weight availability:

- AutoGaze: downloaded.
- OneVision-Encoder: downloaded.
- LLaVA-OV2: downloaded.
