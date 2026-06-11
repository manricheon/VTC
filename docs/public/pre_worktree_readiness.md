# Pre-Worktree Readiness

Status date: `2026-06-11T07:28:02Z`

No model inference was run. Model weights were downloaded under `weights/checkpoints/` because the explicit download flags were set. Heavy model env sync was not run because `VTC_ALLOW_HEAVY_ENV_SYNC` is not set.

## Final Readiness Summary

`READY_FOR_WORKTREE=1` for Project A and Project B artifact-contract worktrees.

This readiness does not mean model-runtime readiness. It means the pure-Python bridge, synthetic smokes, profiling outputs, public blocker docs, and source snapshots are in place for parallel pre-runtime work.

## Resolved For Worktree Start

- bridge-core tests pass.
- Project A synthetic codec smoke passes and emits profile/stat artifacts.
- Project B synthetic OV-direct smoke passes and emits profile/stat artifacts.
- External source snapshots are present under `external/`.
- AutoGaze repo candidate is verified as `nvidia/AutoGaze`.
- AutoGaze, OneVision-Encoder, and LLaVA-OV2 weights are present under `weights/checkpoints/`.
- HF cache/download policy is documented and points under `weights/`.
- Setup/gate automation exists for doctor, system deps, bridge-core, HF assets, model envs, and pre-worktree readiness.

## Remaining Blockers

- `ffmpeg` is missing on the current host and unverified on Linux.
- Model-specific envs are not synced with heavy dependencies.
- Attention fallback is source-audited but not runtime-probed.
- CUDA is unverified.
- MPS is optional and not an official target.
- `lmms-eval` remains deferred until LLaVA-OV2 runtime works.

## Manual Actions

Install/verify `ffmpeg` on Linux:

```bash
bash scripts/check_system_deps.sh
```

Re-run or refresh weights only when explicitly allowed:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_AUTOGAZE=1 \
VTC_DOWNLOAD_OV_ENCODER=1 \
VTC_DOWNLOAD_LLAVA_OV2=1 \
VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 \
bash scripts/setup_hf_assets.sh
```

Sync/probe model envs only when explicitly allowed:

```bash
VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh
```

Run the gate:

```bash
bash scripts/pre_worktree_gate.sh
```

## Worktree Start Order

1. Project A artifact-contract integration.
2. Project B artifact-contract integration.
3. `envs/ov-encoder` import/fallback probe.
4. `envs/llava-ov2` import/codec dependency probe.
5. `envs/autogaze` generation environment setup.
6. `envs/lmms-eval` benchmark/profiling integration.
