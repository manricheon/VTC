# User-Facing Readiness

Date: 2026-06-12

## What Users Can Run Today

Users can run the bridge-core path:

- pure Python tests
- Project A synthetic codec smoke
- Project A LLaVA boundary smoke
- Project B synthetic OV-direct smoke
- Project B OV boundary smoke
- profile summaries for synthetic smoke outputs

These commands do not run AutoGaze, LLaVA-OV2 generation, OneVision-Encoder
forward, or full lmms-eval.

## Boundary-Ready

Project A is boundary-ready for:

```text
decoded_entries -> selected_112_blocks -> src_positions -> LLaVA-compatible payload
```

Project B is boundary-ready for:

```text
decoded_entries -> patches -> patch_positions -> pack_plan
```

The boundary smokes validate artifact contracts and source-inspect external model
code. They do not prove model runtime.

## Not Runtime-Ready Yet

The repository is not yet runtime-ready for:

- real AutoGaze inference
- real LLaVA-OV2 generation
- real OV-Encoder forward
- full lmms-eval benchmark execution

## What Needs Linux/CUDA

Official runtime validation should happen on Linux. CUDA is expected for the
default FlashAttention-oriented model paths unless an isolated probe proves
`sdpa` or `eager` works for a specific model path.

## What Needs Model Env Sync

The following envs need isolated sync/import probes before runtime claims:

- `envs/autogaze`
- `envs/ov-encoder`
- `envs/llava-ov2`
- `envs/lmms-eval`

Do not merge those dependencies into `envs/bridge-core`.

## What Needs ffmpeg

`ffmpeg` is available on the current macOS probe host, but it still needs
verification on the official Linux target. Codec backend and video benchmark
work should treat `ffmpeg` as required.

## What Needs Benchmark Datasets

lmms-eval is not benchmark-ready until the target task datasets are available
and the LLaVA-OV2 runtime path has passed at least a `--limit 1` smoke.

## Expected Artifacts

Project A synthetic outputs:

- `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/decoded_entries.json`
- `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/selected_blocks.json`
- `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/src_positions.npy`
- `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/stats.json`
- `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/profile.json`

Project B synthetic outputs:

- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/decoded_entries.json`
- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/patches.npy`
- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/patch_positions.npy`
- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/pack_plan.json`
- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/stats.json`
- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json`

These outputs are ignored by git and must not be committed.
