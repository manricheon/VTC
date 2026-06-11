# VTC

VTC is a Linux-target, uv-managed multi-project workspace for video token compression experiments and related subprojects.

The first subproject is `projects/gaze-ov-bridge`, which restarts the AutoGaze, OneVision-Encoder, and LLaVA-OV2 work from a clean, staged foundation.

Start with the bridge-core environment guide: [docs/public/environment.md](docs/public/environment.md).

## Repository Layout

- `projects/gaze-ov-bridge/` - first bridge subproject.
- `envs/` - uv-managed environment definitions and setup notes.
- `external/` - third-party source repositories. Do not clone repositories here unless explicitly requested.
- `weights/` - Hugging Face weights, checkpoints, and caches. Do not download model weights unless explicitly requested.
- `artifacts/` - cross-environment JSON/NPY artifacts.
- `artifacts/profiles/` - profiling JSON/JSONL summaries.
- `scripts/` - public development utilities.
- `docs/public/` - public documentation.

Linux is the official target. MacBook/MPS may be used for lightweight probes when possible, but initial setup must not assume CUDA.

## Storage Policy

- `external/` stores third-party source repositories. Do not clone repositories here unless explicitly requested.
- `weights/` stores Hugging Face caches, checkpoints, and model weights. All HF cache paths should resolve under this directory.
- `artifacts/` stores cross-environment JSON/NPY artifacts.
- `artifacts/profiles/` stores profiling JSON/JSONL summaries.

Bridge-core development intentionally excludes `torch`, `transformers`, AutoGaze, OneVision-Encoder, LLaVA-OV2, `lmms-eval`, and `flash_attn`.

## Current Status

The repository is boundary-ready for pure Python bridge development:

- Project A synthetic codec path works.
- Project A LLaVA boundary validation works without generation.
- Project B synthetic OV-direct path works.
- Project B OV boundary validation works without OV-Encoder forward.
- Profile summaries work for current smoke profiles.

It is not runtime-ready for real model inference yet. Real AutoGaze inference,
LLaVA-OV2 generation, OV-Encoder forward, and full `lmms-eval` remain deferred
until Linux/CUDA, model-env sync, attention backend, and dataset/runtime gates
are verified.

See [docs/public/current_status.md](docs/public/current_status.md) and
[docs/public/user_facing_readiness.md](docs/public/user_facing_readiness.md).

## Quickstart

```bash
bash scripts/install_uv_linux.sh
source scripts/env_weights.sh
bash scripts/setup_bridge_core.sh
bash scripts/run_all_smokes.sh
bash scripts/run_profile_summaries.sh
```

For details, see [docs/public/quickstart.md](docs/public/quickstart.md).

## What Works Today

- CPU-safe bridge-core tests.
- Synthetic Project A and Project B smokes.
- Artifact-boundary validation for LLaVA-OV2 and OV-Encoder paths.
- JSON/NPY artifact helpers.
- Profiling schema and summary scripts.

## What Is Deferred

- Heavy model environment runtime validation.
- AutoGaze real output generation.
- LLaVA-OV2 real generation.
- OV-Encoder real forward.
- lmms-eval benchmark execution.

## Agent Handoff

Another developer or coding agent should start with
[docs/public/agent_handoff.md](docs/public/agent_handoff.md).
