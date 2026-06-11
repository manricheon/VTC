# Synthetic Smoke Status

Check date: `2026-06-11T13:12:23Z`

Branch: `feature/gaze-ov-bridge-local`

Commit checked: `6e8a2de`

No real model inference was run. Smoke outputs are under `projects/gaze-ov-bridge/out/` and are intentionally not committed.

## Commands Run

```bash
cd envs/bridge-core
uv run pytest ../../projects/gaze-ov-bridge/tests
uv run python -m compileall ../../projects/gaze-ov-bridge/src
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py
uv run python ../../scripts/profile_summary.py \
  ../../projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/profile.json \
  ../../projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json || true
cd ../..
```

Results:

- `pytest`: 37 passed.
- `compileall`: passed.
- Project A smoke: passed.
- Project B smoke: passed.
- Profile summary: parsed both smoke profiles.

## Project A Codec Smoke

Status: `pass`

Track: `project_a_codec`

Policy: `anchor112_default`

Artifacts:

- `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/stats.json`
- `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/profile.json`
- `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/decoded_entries.json`
- `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/selected_blocks.json`
- `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/src_positions.npy`

Token/profile summary:

- valid AutoGaze tokens: 5
- selected 112 blocks: 2
- raw patch tokens: 8
- LLM visual tokens: 2
- Project A vs dense raw ratio: 0.015625
- Project A vs dense visual ratio: 0.015625
- no-hard-union default: confirmed

Readiness: ready for Project A artifact-contract work; not a real LLaVA-OV2 runtime proof.

## Project B OV-Direct Smoke

Status: `pass`

Track: `project_b_ov_direct`

Policy: `direct_multiscale_no_union`

Artifacts:

- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/stats.json`
- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json`
- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/decoded_entries.json`
- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/patch_positions.npy`
- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/patches.npy`
- `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/pack_plan.json`

Token/profile summary:

- direct tokens: 5
- tokens by scale: `{28: 2, 56: 1, 112: 1, 224: 1}`
- Project B vs AutoGaze candidates ratio: 0.007353
- Project B vs dense native ratio: 0.009766
- no-native-union default: confirmed

Readiness: ready for Project B artifact-contract work; not a real OV-Encoder forward proof.
