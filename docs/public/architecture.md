# Architecture

VTC is a multi-project workspace. The first subproject is
`projects/gaze-ov-bridge`.

## Directory Layout

- `external/`: third-party source repositories and code-only snapshots.
- `weights/`: Hugging Face caches, checkpoints, and model weights.
- `artifacts/`: cross-environment JSON/NPY artifacts.
- `artifacts/profiles/`: cross-run profiling JSON/JSONL outputs.
- `envs/`: isolated uv environments.
- `projects/gaze-ov-bridge/`: bridge source, tests, scripts, and subproject docs.
- `docs/public/`: shareable documentation.
- `scripts/`: repository-level public utilities.

`external/`, `weights/`, `artifacts/`, and `projects/gaze-ov-bridge/out/` are
not committed.

## Environment Split

- `envs/bridge-core`: pure Python bridge logic, synthetic tests, profiles.
- `envs/autogaze`: real AutoGaze output generation.
- `envs/ov-encoder`: OneVision-Encoder direct runtime.
- `envs/llava-ov2`: LLaVA-OV2 processor/backend/generation runtime.
- `envs/lmms-eval`: benchmark runtime.
- `envs/mps-probe`: optional Mac/MPS diagnostics.

Use JSON/NPY artifacts between envs instead of importing model packages across
environment boundaries.

## Artifact Exchange

AutoGaze outputs:

- `artifacts/autogaze/<video_id>/gazing_pos.npy`
- `artifacts/autogaze/<video_id>/if_padded_gazing.npy`
- `artifacts/autogaze/<video_id>/decoded_entries.json`

Project A codec artifacts:

- `artifacts/project_a_codec/<video_id>/selected_blocks.json`
- `artifacts/project_a_codec/<video_id>/src_positions.npy`
- `artifacts/project_a_codec/<video_id>/stats.json`

Project B OV-direct artifacts:

- `artifacts/project_b_ov_direct/<video_id>/patches.npy`
- `artifacts/project_b_ov_direct/<video_id>/patch_positions.npy`
- `artifacts/project_b_ov_direct/<video_id>/stats.json`

## Project A Flow

```text
decoded_entries -> selected_112_blocks -> src_positions -> LLaVA-compatible payload
```

Rules:

- `112` scale is the canonical anchor.
- `224` scale is fine evidence for the containing 112 block.
- `56` scale is a region prior.
- `28` scale is a frame/global prior.
- hard union exists only as an explicit ablation.

## Project B Flow

```text
decoded_entries -> patches -> patch_positions -> pack_plan
```

Rules:

- preserve one AutoGaze selected token as one OV token.
- do not expand coarse tokens into native-grid union.
- keep fractional `patch_positions = [t, h, w]` explicit.

## Profiling Schema Summary

Profiles include:

- run metadata
- environment metadata
- input metadata
- token counts
- compression ratios
- timings by stage
- memory where available
- task metrics where available

See `docs/public/profiling.md` for full definitions.
