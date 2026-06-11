# Pre-Worktree Readiness

Status date: `2026-06-11T13:12:23Z`

No model inference was run. No new weights were downloaded in this pass. No external repos were cloned in this pass.

## Final Decision

`READY_FOR_WORKTREE=yes`

`bash scripts/pre_worktree_gate.sh` reports:

```text
READY_FOR_WORKTREE=1
```

This means Project A and Project B artifact-contract worktrees may start. It does not mean model-runtime readiness.

## Project Readiness

| Area | Readiness | Evidence | Remaining blocker |
| --- | --- | --- | --- |
| Project A: AutoGaze -> LLaVA-OV2 codec-compatible | ready for artifact-contract work | tests pass; Project A smoke/profile pass; `src_positions.npy` produced | real codec/backend runtime needs `ffmpeg`, env sync, import probe, attention backend verification |
| Project B: AutoGaze -> OV-Encoder direct | ready for artifact-contract work | tests pass; Project B smoke/profile pass; `patch_positions.npy`, `patches.npy`, and `pack_plan.json` produced | real OV-Encoder forward needs env sync/import probe and attention backend verification |
| lmms-eval | not ready for benchmark work | source and adapter exist; no full benchmark run | wait for Project A runtime path, env sync, `ffmpeg`, and attention backend verification |

## Current Status

External source status:

- `external/AutoGaze`: present.
- `external/LLaVA-OneVision-2`: present.
- `external/lmms-eval`: present.
- `external/LLaVA-OneVision-2-8B-Instruct-code`: present.
- `external/OneVision-Encoder`: present.

Weights status:

- AutoGaze: payload present, 13M.
- OneVision-Encoder: payload present, 602M.
- LLaVA-OV2: payload present, 16G.

System dependency status:

- `ffmpeg`: missing on current Mac probe host; Linux target unverified.
- `uv`, `git`, `curl`, `bash`: available on current host.

Model env status:

- `bridge-core`: ready.
- model envs: no heavy sync; no-sync probes are partial only.

Attention fallback status:

- source suggests SDPA/eager fallback paths for OV-Encoder and LLaVA-OV2.
- runtime fallback is unverified.
- lmms-eval adapter defaults toward `flash_attention_2`.
- CUDA/flash-attn readiness is unverified.

Profiling status:

- profile schema/utilities exist.
- Project A and Project B smoke profiles exist.
- `profile_summary.py` parses both smoke profiles.
- process RSS and tracemalloc are available.
- CUDA/MPS memory metrics require torch in the matching env.

## Remaining Blockers

- Install/verify `ffmpeg` on Linux before codec/backend runtime tests.
- Sync/probe model envs separately before import/runtime claims.
- Verify exact attention backend (`flash_attention_2`, `sdpa`, or `eager`) per model path.
- Run CUDA checks only on the Linux CUDA target.
- Treat MPS as best-effort only.

## Exact Manual Actions

Linux system dependency:

```bash
bash scripts/check_system_deps.sh
```

Model env probes:

```bash
VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh
```

No-sync probe refresh:

```bash
RUN_UV_PROBES=1 RUN_OPTIONAL_MPS=1 bash scripts/run_compat_probes.sh
```

Final gate:

```bash
bash scripts/pre_worktree_gate.sh
```
