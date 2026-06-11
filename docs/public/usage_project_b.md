# Usage: Project B

Project B converts AutoGaze-style artifacts into OneVision-Encoder direct
artifacts while preserving one selected AutoGaze token as one OV token.

```text
AutoGaze artifact -> multi-scale patch tokens -> fractional patch_positions -> OV direct boundary
```

This is currently boundary-ready, not OV-forward-ready.

## Expected Inputs

- `decoded_entries.json`
- `patches.npy`
- `patch_positions.npy`
- `pack_plan.json`

For the current smoke, these are produced under:

```text
projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/
```

## Expected Outputs

- `stats.json`
- `profile.json`

Boundary smoke outputs go under:

```text
projects/gaze-ov-bridge/out/smoke_project_b_ov_boundary/
```

## Commands

```bash
cd envs/bridge-core
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_boundary.py
uv run python ../../scripts/profile_summary.py \
  ../../projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json \
  ../../projects/gaze-ov-bridge/out/smoke_project_b_ov_boundary/profile.json
cd ../..
```

Or from the repository root:

```bash
bash scripts/run_project_b_examples.sh
bash scripts/run_profile_summaries.sh
```

## Token Definitions

- `valid AutoGaze tokens`: decoded entries with padding removed.
- `OV direct tokens`: one token per valid AutoGaze entry.
- `dense_native_raw_patch_tokens = num_frames * 16 * 16`.

## Compression Definitions

- `project_b_vs_autogaze_candidates_ratio = project_b_ov_direct_tokens / autogaze_candidate_tokens_total`
- `project_b_vs_dense_native_ratio = project_b_ov_direct_tokens / dense_native_raw_patch_tokens`
- reductions are `1 - ratio`

## Current Blockers For Real OV Forward

- `envs/ov-encoder` must be fully synced/probed.
- Attention backend must be verified at runtime.
- Linux/CUDA target must be checked for real forward runs.
- Project B smokes do not import OneVision-Encoder or run model forward.
