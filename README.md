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
