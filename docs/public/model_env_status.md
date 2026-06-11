# Model Environment Status

Status date: `2026-06-11T13:12:23Z`

No heavy model environment sync was run in this pass. The no-sync compatibility probes were run with:

```bash
RUN_UV_PROBES=1 RUN_OPTIONAL_MPS=1 bash scripts/run_compat_probes.sh
```

This does not install dependencies and does not run model inference.

## Summary

| Env | uv sync status | Probe status | Current blocker | Next command |
| --- | --- | --- | --- | --- |
| `envs/bridge-core` | synced | pass | none for pure-Python bridge work | `bash scripts/setup_bridge_core.sh` |
| `envs/autogaze` | not synced | partial | `torch`, `transformers`, `flash_attn`, video deps absent; fallback unverified | `VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh` |
| `envs/ov-encoder` | not synced | partial | `torch`/`transformers` absent; SDPA/eager runtime fallback unverified | `VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh` |
| `envs/llava-ov2` | not synced | partial | `torch`, `transformers`, codec/video deps, and `ffmpeg` absent/unverified | `VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh` |
| `envs/lmms-eval` | not synced | partial | benchmark deps absent; adapter import blocked by missing deps such as `loguru` | defer until LLaVA-OV2 runtime path works |
| `envs/mps-probe` | not synced | optional partial | `torch` absent, so MPS availability cannot be checked | optional only; not official support |

## Weight Availability

All three expected checkpoint directories contain recognized payload files:

| Target | Status | Local size |
| --- | --- | --- |
| AutoGaze | payload present | 13M |
| OneVision-Encoder | payload present | 602M |
| LLaVA-OV2 | payload present | 16G |

Weights are not committed and remain under `weights/`.

## Profiling Capability

No-sync probes confirm:

- process RSS: available
- `tracemalloc`: available
- torch CUDA memory: unavailable until torch is installed in the target env
- torch MPS memory: unavailable until torch is installed in the optional MPS env

## Readiness Decision

Ready:

- `envs/bridge-core` is ready for Project A/B artifact-contract work.

Not ready:

- `envs/autogaze` is not ready for real AutoGaze generation.
- `envs/ov-encoder` is not ready for real OV-Encoder forward.
- `envs/llava-ov2` is not ready for real LLaVA-OV2 generation.
- `envs/lmms-eval` is not ready for full benchmarks.
- `envs/mps-probe` is optional and not an official gate.
