# Compatibility Probe Results

Probe date: `2026-06-11T13:12:23Z`

No additional weights were downloaded. No full model inference was run. No full `lmms-eval` benchmark was run.

Commands:

```bash
bash scripts/run_compat_probes.sh || true
RUN_UV_PROBES=1 RUN_OPTIONAL_MPS=1 bash scripts/run_compat_probes.sh || true
```

Default mode prints commands only. The second command uses `uv run --no-sync`, so it does not install heavy dependencies.

Runtime artifacts:

- `artifacts/compat/*_probe.json`
- `artifacts/profiles/compat_*.json`

These are ignored by git.

## Summary

| Env | Status | Main blockers | Weight status | Profiling capability | Next action |
| --- | --- | --- | --- | --- | --- |
| `bridge-core` | pass | none for pure-Python work | not needed | profile summary works | Continue Project A/B bridge work. |
| `autogaze` | partial | deps not synced; `torch`, `transformers`, `flash_attn`, video libs absent; `ffmpeg` absent | payload present | RSS/tracemalloc available; torch memory unavailable | Sync/probe on Linux before generation. |
| `ov_encoder` | partial | deps not synced; `torch`/`transformers` absent; fallback unverified | payload present | RSS/tracemalloc available; torch memory unavailable | Sync/probe and verify SDPA/eager. |
| `llava_ov2` | partial | deps not synced; video/codec deps absent; `ffmpeg` absent; fallback unverified | payload present | RSS/tracemalloc available; torch memory unavailable | Install/verify `ffmpeg`, sync/probe, then processor/backend import tests. |
| `lmms_eval` | partial | benchmark deps absent; adapter import blocked by missing deps | model payloads present for target model, env not ready | RSS/tracemalloc available; torch memory unavailable | Defer until Project A runtime path works. |
| `mps_probe` | optional partial | torch absent, MPS cannot be checked | payloads present but not used | RSS/tracemalloc available; MPS memory unavailable | Optional only. |

## Key Findings

- External source paths are present.
- HF cache paths are under `weights/`.
- Weight directories contain recognized payload files.
- `ffmpeg` is absent on this host.
- `flash_attn` is not importable in unsynced envs.
- Source suggests SDPA/eager fallback paths for OV-Encoder and LLaVA-OV2, but runtime fallback is not verified.
- lmms-eval has latency/token hook references but defaults toward `flash_attention_2`.

## Interpretation

These probes are sufficient for pre-worktree artifact-contract work. They are not sufficient for model-runtime readiness.

Before real model execution:

1. Install/verify `ffmpeg` on Linux.
2. Sync/probe each model env separately.
3. Verify processor/model imports without inference.
4. Record the exact attention backend used.
