# gaze-ov-bridge Project Plan

`gaze-ov-bridge` rebuilds the previous AutoGaze / OneVision-Encoder / LLaVA-OV2 experiments in staged, auditable increments.

## Engineering Workflow

- Keep implementation simple and contract-first.
- Prefer functions over classes unless state is necessary.
- Avoid unnecessary abstraction and silent fallback.
- Use `$karpathy-engineering` before substantial development, refactor, blocker resolution, model integration, and worktree handoff.
- Verify changes with focused tests, synthetic smoke, profile output, or documented blocker evidence.
- Keep local guidance commits separate from public source/test/script/doc commits.

## Project A First: AutoGaze -> LLaVA-OV2 Codec-Compatible Path

1. Define the artifact schema for AutoGaze selections and frame metadata.
2. Build pure Python synthetic fixtures for multi-scale AutoGaze-like selections.
3. Implement conversion from AutoGaze selections to 112-anchor LLaVA-OV2 units.
4. Validate integer `src_positions` and native 2x2 patch ordering with synthetic tests.
5. Add smoke scripts that emit `stats.json`.
6. Audit LLaVA-OV2 dependency and attention backend requirements before model setup.
7. Integrate real LLaVA-OV2 code only after artifact conversion and profiling tests are stable.
8. Add answer-level score evaluation.
9. Add lmms-eval integration later.

## Project B Second: AutoGaze -> OneVision-Encoder Direct Path

1. Define direct OV-Encoder artifact schema for scale-resized 14x14 patches.
2. Build synthetic tests that preserve one AutoGaze selected token as one OV-Encoder token.
3. Implement fractional `patch_positions = [t, h, w]`.
4. Validate scale-grid position mapping against the native 224/14 grid.
5. Add direct-vs-dense token accounting.
6. Audit OneVision-Encoder dependency and attention backend requirements before model setup.
7. Integrate real OV-Encoder code only after synthetic tests and profiling are stable.

## Profiling Before Model Integration

Define the profiling schema before loading real models. Every smoke script and real integration script must write `stats.json`; real model scripts should write `profile.json` or `profile.jsonl`.

Profiling must capture wall-clock timings by stage, token counts, compression ratios, peak CPU memory where possible, CUDA/MPS memory where possible, environment metadata, git commit, and `run_id`.

Use stdlib profiling first. Collect torch-specific memory metrics only when torch is installed.

## Test Order

- Synthetic tests before real model tests.
- CPU-safe pure Python tests first.
- MacBook/MPS probes only when dependencies and attention backends allow them.
- Linux remains the official target.

## Dependency Compatibility Audit

Perform a dependency compatibility audit before heavy environment setup. Do not add or install `torch`, `transformers`, AutoGaze, OneVision-Encoder, LLaVA-OV2, `lmms-eval`, `flash_attn`, or model weights until explicitly requested.

## Storage Policy

- `external/` stores third-party source repositories.
- `weights/` stores Hugging Face weights, checkpoints, and caches.
- `artifacts/` stores cross-environment JSON/NPY artifacts.
- `artifacts/profiles/` stores profiling summaries.
- Use JSON/NPY artifacts between environments instead of importing model packages across environments.

## Public Branch Policy

Local guidance commits must be excluded from any later public remote branch.
