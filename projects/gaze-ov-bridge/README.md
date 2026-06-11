# gaze-ov-bridge

`gaze-ov-bridge` is the first VTC subproject. It will rebuild prior AutoGaze, OneVision-Encoder, and LLaVA-OV2 experiments through small, auditable stages.

The package starts with CPU-safe Python scaffolding only. Heavy model dependencies, external repositories, and model weights are intentionally excluded from the initial setup.

## Priorities

Project A is first: AutoGaze outputs become LLaVA-OV2 codec-compatible 112-anchor block selections for answer-level scoring and later `lmms-eval`.

Project B is second: AutoGaze outputs become OneVision-Encoder direct sparse patch tokens for feature-level analysis.

## Bridge-Core Tests

From the VTC repository root:

```bash
bash scripts/bootstrap_bridge_core.sh
```

On a non-Linux development machine, this is a best-effort probe and requires:

```bash
ALLOW_NON_LINUX=1 bash scripts/bootstrap_bridge_core.sh
```

The bootstrap uses `uv sync` and `uv run`; it does not call `pip`, create a virtualenv manually, install model dependencies, clone repositories, download weights, or run real model inference.

## Environment Isolation

Model-specific dependencies are isolated under `envs/*`.

- `envs/bridge-core` is for pure Python bridge code, synthetic tests, and profiling schema work.
- `envs/autogaze` will be for actual AutoGaze output generation.
- `envs/ov-encoder` will be for OneVision-Encoder direct forward probes.
- `envs/llava-ov2` will be for LLaVA-OV2 processor/backend/generation work.
- `envs/lmms-eval` will be for benchmark execution.
- `envs/mps-probe` is optional and best-effort only.

Profiling is part of every smoke and integration stage. Synthetic smoke scripts should produce `stats.json`; real model scripts should later produce `profile.json` or `profile.jsonl`.

## Initial Constraints

- Python `>=3.11`.
- Managed with `uv`.
- Runtime dependencies are limited to `numpy>=1.24` and `pillow>=10.0`.
- Test dependency is limited to `pytest>=8.0`.
- Do not add `torch`, `transformers`, AutoGaze, OneVision-Encoder, LLaVA-OV2, `lmms-eval`, or `flash_attn` yet.

## Current Usage

Project A usage:

```bash
bash scripts/run_project_a_examples.sh
```

This runs the synthetic codec smoke and LLaVA boundary validation. It does not
run LLaVA-OV2 generation. See
[docs/public/usage_project_a.md](../../docs/public/usage_project_a.md).

Project B usage:

```bash
bash scripts/run_project_b_examples.sh
```

This runs the synthetic OV-direct smoke and OV boundary validation. It does not
run OV-Encoder forward. See
[docs/public/usage_project_b.md](../../docs/public/usage_project_b.md).

All current safe smokes:

```bash
bash scripts/run_all_smokes.sh
bash scripts/run_profile_summaries.sh
```

## Boundary vs Runtime

The current bridge is boundary-ready:

- Project A validates `decoded_entries -> selected_112_blocks -> src_positions -> LLaVA-compatible payload`.
- Project B validates `decoded_entries -> patches -> patch_positions -> pack_plan`.

The bridge is not yet runtime-ready for real AutoGaze, LLaVA-OV2,
OneVision-Encoder, or lmms-eval execution. Those paths require isolated model
env sync, Linux runtime checks, attention backend verification, and model/dataset
runtime gates.
