# Usage: Project A

Project A converts AutoGaze-style artifacts into a LLaVA-OV2
codec-compatible boundary payload.

```text
AutoGaze artifact -> 112-anchor selected blocks -> src_positions -> LLaVA-compatible payload
```

This is currently boundary-ready, not generation-ready.

## Expected Inputs

Synthetic or serialized AutoGaze-side artifacts:

- `decoded_entries.json`
- `selected_blocks.json`
- `src_positions.npy`

For the current smoke, these are produced under:

```text
projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/
```

## Expected Outputs

- `stats.json`
- `profile.json`

Boundary smoke outputs go under:

```text
projects/gaze-ov-bridge/out/smoke_project_a_llava_boundary/
```

## Commands

```bash
cd envs/bridge-core
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_llava_boundary.py
uv run python ../../scripts/profile_summary.py \
  ../../projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/profile.json \
  ../../projects/gaze-ov-bridge/out/smoke_project_a_llava_boundary/profile.json
cd ../..
```

Or from the repository root:

```bash
bash scripts/run_project_a_examples.sh
bash scripts/run_profile_summaries.sh
```

## Token Definitions

- `selected_112_blocks`: final 112-anchor blocks selected for LLaVA-OV2.
- `raw_patch_tokens = selected_112_blocks * 4`.
- `llm_visual_tokens = selected_112_blocks`.
- Dense raw comparison: `num_frames * 16 * 16`.
- Dense visual comparison: `num_frames * 8 * 8`.

## Compression Definitions

- `project_a_vs_dense_raw_ratio = raw_patch_tokens / dense_native_raw_patch_tokens`
- `project_a_vs_dense_visual_ratio = llm_visual_tokens / dense_native_merged_visual_tokens`
- reductions are `1 - ratio`

## Current Blockers For Real Generation

- `envs/llava-ov2` must be fully synced/probed.
- Attention backend must be verified at runtime.
- Linux/CUDA target must be checked for real generation.
- Real AutoGaze outputs must be generated or supplied.
- LLaVA-OV2 generation and lmms-eval are not run by Project A smokes.
