# VTC Agent Guidance

VTC is a large project with multiple subprojects.

The first subproject is `projects/gaze-ov-bridge`.

## Targets

- Official target is Linux.
- MacBook / MPS may be used for lightweight probes if possible.
- Do not assume CUDA during initial development.
- Prefer CPU/MPS-safe pure Python tests first.

## Repository Policy

- `external/` stores third-party source repos.
- `weights/` stores HF weights, checkpoints, and caches.
- `artifacts/` stores cross-environment JSON/NPY artifacts.
- `artifacts/profiles/` stores profiling summaries.
- All HF downloads must go under `weights/`.
- Do not clone external repos or download weights unless explicitly requested.

## Commit Policy

- `AGENTS.md`, `PROJECT_PLAN.md`, prompts, and `docs/local` are committed locally but must remain in separate guidance commits.
- Public branches must exclude local guidance commits.
- Environment scripts and profiling scripts are public development utilities and may be committed separately from guidance files.
