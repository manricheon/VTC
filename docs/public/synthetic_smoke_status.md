# Synthetic Smoke Status

Check date: `2026-06-11T06:26:52Z`

Branch: `feature/gaze-ov-bridge-local`

Base commit checked: `8bb4123`

This pass re-ran the bridge-core test suite and both synthetic smoke scripts after the external source, system dependency, compatibility probe, and weight-download status work. No real model inference was run and no additional weights were downloaded.

## Commands Run

```bash
cd envs/bridge-core
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run pytest ../../projects/gaze-ov-bridge/tests
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run python ../../scripts/profile_summary.py \
  ../../projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/profile.json \
  ../../projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run python -m compileall ../../projects/gaze-ov-bridge/src
cd ../..
```

Verification results:

- `pytest`: `35 passed in 0.50s`
- Project A smoke: completed
- Project B smoke: completed
- `profile_summary.py`: parsed both generated smoke profiles
- `compileall`: completed for `projects/gaze-ov-bridge/src`

Generated smoke outputs are under `projects/gaze-ov-bridge/out/` and are intentionally not committed.

## Project A Codec Smoke

Status: `pass`

Track: `project_a_codec`

Policy: `anchor112_default`

Output directory:

```text
projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/
```

Key artifacts:

- `stats.json`
- `profile.json`
- `decoded_entries.json`
- `selected_blocks.json`
- `src_positions.npy`

Token counts:

| Metric | Value |
| --- | ---: |
| AutoGaze candidate tokens total | 680 |
| AutoGaze valid tokens total | 5 |
| Dense native raw patch tokens | 512 |
| Dense native merged visual tokens | 128 |
| Selected 112 blocks | 2 |
| Project A raw patch tokens | 8 |
| Project A LLM visual tokens | 2 |

AutoGaze candidate tokens by scale:

| Scale | Candidate tokens |
| --- | ---: |
| 28 | 8 |
| 56 | 32 |
| 112 | 128 |
| 224 | 512 |

Decoded valid entries by scale:

| Scale | Valid entries |
| --- | ---: |
| 28 | 2 |
| 56 | 1 |
| 112 | 1 |
| 224 | 1 |

Compression:

| Metric | Value |
| --- | ---: |
| Project A vs dense raw ratio | 0.015625 |
| Project A raw reduction | 0.984375 |
| Project A vs dense visual ratio | 0.015625 |
| Project A visual reduction | 0.984375 |

Timings:

| Stage | Seconds |
| --- | ---: |
| total | 0.002017 |
| decode | 0.000074 |
| selector | 0.000157 |
| src_positions | 0.000020 |

Memory:

| Metric | MB |
| --- | ---: |
| process_peak_rss | 30.0625 |
| tracemalloc_peak | 0.0390 |
| cuda_peak_allocated | null |
| cuda_peak_reserved | null |
| mps_current_allocated | null |

No-hard-union confirmation:

- `confirms_no_hard_union_default = true`
- 56-scale and 28-scale tokens remain priors under the default policy.
- Selected units are 112 blocks, with each selected block mapping to four native 14x14 patches.

Readiness:

- Ready as a pure-Python codec-compatible artifact generator for later `envs/llava-ov2` work.
- Not ready for real LLaVA-OV2 processor/generation until model dependencies, weights, ffmpeg, and attention backend behavior are verified.

## Project B OV-Direct Smoke

Status: `pass`

Track: `project_b_ov_direct`

Policy: `direct_multiscale_no_union`

Output directory:

```text
projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/
```

Key artifacts:

- `stats.json`
- `profile.json`
- `decoded_entries.json`
- `patch_positions.npy`
- `patches.npy`
- `pack_plan.json`

Token counts:

| Metric | Value |
| --- | ---: |
| AutoGaze candidate tokens total | 680 |
| AutoGaze valid tokens total | 5 |
| Dense native raw patch tokens | 512 |
| Project B OV-direct tokens | 5 |
| Patch positions shape | `[5, 3]` |
| Patches shape | `[5, 14, 14, 3]` |
| Pack canvas count | 1 |

Selected tokens by scale:

| Scale | Direct tokens |
| --- | ---: |
| 28 | 2 |
| 56 | 1 |
| 112 | 1 |
| 224 | 1 |

Compression:

| Metric | Value |
| --- | ---: |
| Project B vs AutoGaze candidates ratio | 0.007352941176470588 |
| Project B reduction vs candidates | 0.9926470588235294 |
| Project B vs dense native ratio | 0.009765625 |
| Project B reduction vs dense native | 0.990234375 |

Timings:

| Stage | Seconds |
| --- | ---: |
| total | 0.004867 |
| decode | 0.000185 |
| patch_extract | 0.002341 |
| pack | 0.000010 |

Memory:

| Metric | MB |
| --- | ---: |
| process_peak_rss | 33.546875 |
| tracemalloc_peak | 0.7315 |
| cuda_peak_allocated | null |
| cuda_peak_reserved | null |
| mps_current_allocated | null |

No-native-union confirmation:

- `confirms_no_native_union = true`
- Each valid AutoGaze token maps to exactly one OV-direct token.
- Coarse 28/56/112 scale tokens are not expanded into native 224-grid patch unions.

Readiness:

- Ready as a pure-Python OV-direct artifact generator for later `envs/ov-encoder` work.
- Not ready for real OneVision-Encoder forward until isolated dependencies, weights, and attention backend behavior are verified.

## Model-Env Readiness

The synthetic smoke outputs are ready for model-specific env integration work at the artifact-contract level:

- Project A has `selected_blocks.json`, `src_positions.npy`, `stats.json`, and `profile.json`.
- Project B has `patch_positions.npy`, `patches.npy`, `pack_plan.json`, `stats.json`, and `profile.json`.

The generated artifacts prove the bridge-core data paths, not model runtime behavior.

Remaining blockers before real model-backed work:

- AutoGaze, OV-Encoder, and LLaVA-OV2 weights have not been downloaded.
- Linux `ffmpeg` is still missing or not verified for codec/backend tests.
- Isolated model environments were not synced with heavy dependencies.
- `flash_attn` versus SDPA/eager fallback behavior remains unverified at runtime.
- CUDA availability is unverified on the official Linux target.
- `lmms-eval` remains deferred until model-specific envs are working.

## Recommended Worktree Start Order

1. Project A artifact-contract worktree: wire codec-compatible smoke outputs into the `envs/llava-ov2` processor/backend boundary without generation.
2. Project B artifact-contract worktree: wire OV-direct `patch_positions.npy` and synthetic patch payloads into the `envs/ov-encoder` boundary without encoder forward.
3. OV-Encoder compatibility worktree: sync/probe `envs/ov-encoder`, verify `transformers==4.57.3`, `patch_positions`, and SDPA/eager behavior.
4. LLaVA-OV2 compatibility worktree: install/verify Linux `ffmpeg`, sync/probe `envs/llava-ov2`, and verify processor/code imports before weight-backed generation.
5. AutoGaze generation worktree: download verified `nvidia/AutoGaze` weights when explicitly allowed, then produce real `gazing_pos` and `if_padded_gazing` artifacts.
6. `lmms-eval` worktree: keep last, after Project A generation path and profiling hooks are validated.
