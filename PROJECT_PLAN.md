# VTC Project Plan

VTC will contain multiple projects.

The first project is `projects/gaze-ov-bridge`.

We will rebuild prior AutoGaze / OneVision-Encoder / LLaVA-OV2 experiments step by step.

## Priorities

Project A has priority: AutoGaze -> LLaVA-OV2 codec-compatible path for score/evaluation.

Project B is second: AutoGaze -> OV-Encoder direct path for feature-level analysis.

## Development Target

- Use Linux + uv as the official development target.
- Allow MacBook/MPS only for lightweight probes when possible.

## Engineering Style

- Keep code simple, explicit, and easy to hand off.
- Prefer small functions over classes unless real state needs a class.
- Avoid unnecessary abstraction and silent fallback.
- Require a reproducible check for nontrivial work: pytest, smoke, profile, or documented blocker.
- Keep public code/docs separate from local guidance commits.
- Use `$karpathy-engineering` for substantial work, refactors, blocker resolution, model integration, and worktree handoff.

## Environments

Use separate environments:

- `envs/bridge-core`
- `envs/autogaze`
- `envs/ov-encoder`
- `envs/llava-ov2`
- `envs/lmms-eval`
- `envs/mps-probe`

## Integration Plan

- Do dependency compatibility audit before model integration.
- Add profiling from the beginning:
  - speed
  - token counts
  - compression ratios
  - memory
  - score trade-offs
- Use JSON/NPY artifacts between environments instead of importing model packages across environments.
