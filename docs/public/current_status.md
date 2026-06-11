# Current Status

Date: 2026-06-12

## Summary

VTC/gaze-ov-bridge is boundary-ready for the pure Python Project A and Project B
contracts. It is not runtime-ready for real model inference or full benchmarks.

## What Works

- bridge-core uv environment
- tests and compile checks
- Project A synthetic codec smoke
- Project A LLaVA boundary smoke
- Project B synthetic OV-direct smoke
- Project B OV boundary smoke
- profile summaries for smoke profiles
- source and weight presence checks
- guarded lmms-eval limit-one runner skeleton

## What Is Boundary-Only

- Project A validates `selected_blocks -> src_positions -> LLaVA-compatible payload`.
- Project B validates `patches + patch_positions + pack_plan -> OV-direct payload`.
- External model source is source-inspected but not imported by bridge-core.

## What Is Not Runtime-Ready

- AutoGaze real inference.
- LLaVA-OV2 real generation.
- OV-Encoder real forward.
- lmms-eval full benchmark.

## External Sources

Expected source paths are present:

- `external/AutoGaze`
- `external/LLaVA-OneVision-2`
- `external/LLaVA-OneVision-2-8B-Instruct-code`
- `external/OneVision-Encoder`
- `external/lmms-eval`

These paths are ignored by git.

## Weights

Expected checkpoint directories contain payload files:

- `weights/checkpoints/AutoGaze`
- `weights/checkpoints/onevision-encoder-large`
- `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct`

Weights are ignored by git.

## Environment Status

- `bridge-core`: ready.
- `autogaze`: not fully synced/probed.
- `ov-encoder`: not fully synced/probed.
- `llava-ov2`: not fully synced/probed.
- `lmms-eval`: not benchmark-ready.
- `mps-probe`: optional only.

## Main Blockers

- Run Linux target gate.
- Sync/probe model envs separately.
- Verify attention backend behavior.
- Run import-only model probes before any real inference.
- Run lmms-eval `--limit 1` only after LLaVA-OV2 runtime works.

## Start Here

```bash
bash scripts/run_all_smokes.sh
bash scripts/run_profile_summaries.sh
```
