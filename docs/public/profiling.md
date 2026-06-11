# Profiling

Profiling is required for every bridge smoke test and every later real integration test. The goal is to make speed, token counts, compression, memory, and score trade-offs visible before model-specific code is introduced.

The bridge-core profiling utilities are stdlib-first and safe for the Level 1 environment. They do not require `torch`, `transformers`, AutoGaze, LLaVA-OV2, OneVision-Encoder, or `lmms-eval`.

## Profile Records

Profile records are JSON-serializable dictionaries with deterministic key ordering when written through `write_profile_json` or `append_profile_jsonl`.

Top-level fields:

- `schema_version`
- `run_id`
- `created_at_utc`
- `git_commit`
- `project`
- `environment`
- `input`
- `token_counts`
- `compression`
- `timings_s`
- `memory_mb`
- `task_metrics`
- `notes`

Supported tracks:

- `project_a_codec`
- `project_b_ov_direct`
- `autogaze`
- `llava_ov2`
- `ov_encoder`
- `lmms_eval`
- `compat_probe`

## Token Definitions

AutoGaze candidate tokens per frame:

```text
sum((scale // patch_size)^2 for scale in target_scales)
```

The default `target_scales=[28, 56, 112, 224]` and `patch_size=14` produce `340` candidate tokens per frame.

Dense native raw patch tokens:

```text
num_frames * 16 * 16
```

Dense native merged visual tokens for LLaVA-OV2:

```text
num_frames * 8 * 8
```

Project A token counts:

```text
project_a_raw_patch_tokens = selected_112_blocks * 4
project_a_llm_visual_tokens = selected_112_blocks
```

Project B token count:

```text
project_b_ov_direct_tokens = autogaze_valid_tokens_total
```

## Compression Definitions

All divisions are safe. A zero or missing denominator produces `null`.

Project A:

```text
project_a_vs_dense_raw_ratio = project_a_raw_patch_tokens / dense_native_raw_patch_tokens
project_a_vs_dense_visual_ratio = project_a_llm_visual_tokens / dense_native_merged_visual_tokens
project_a_raw_reduction = 1 - project_a_vs_dense_raw_ratio
project_a_visual_reduction = 1 - project_a_vs_dense_visual_ratio
```

Project B:

```text
project_b_vs_autogaze_candidates_ratio = project_b_ov_direct_tokens / autogaze_candidate_tokens_total
project_b_vs_dense_native_ratio = project_b_ov_direct_tokens / dense_native_raw_patch_tokens
project_b_reduction_vs_candidates = 1 - project_b_vs_autogaze_candidates_ratio
project_b_reduction_vs_dense_native = 1 - project_b_vs_dense_native_ratio
```

## Project A Fields

Project A profiles should set:

- `project.track = "project_a_codec"`
- `input.video_id`
- `input.num_frames`
- `input.target_scales`
- `input.patch_size`
- `token_counts.selected_112_blocks`
- `token_counts.project_a_raw_patch_tokens`
- `token_counts.project_a_llm_visual_tokens`
- `compression.project_a_vs_dense_raw_ratio`
- `compression.project_a_vs_dense_visual_ratio`
- `timings_s.selector`
- `timings_s.src_positions`
- `timings_s.pack`

Later real LLaVA-OV2 runs should also fill `timings_s.processor`, `timings_s.model_forward`, `timings_s.generate`, and task score fields where available.

## Project B Fields

Project B profiles should set:

- `project.track = "project_b_ov_direct"`
- `input.video_id`
- `input.num_frames`
- `input.target_scales`
- `input.patch_size`
- `token_counts.autogaze_valid_tokens_total`
- `token_counts.project_b_ov_direct_tokens`
- `compression.project_b_vs_autogaze_candidates_ratio`
- `compression.project_b_vs_dense_native_ratio`
- `timings_s.selector`
- `timings_s.patch_extract`
- `timings_s.pack`

Later real OV-Encoder runs should also fill `timings_s.model_forward`.

## Memory Metrics and Limitations

`memory_mb.process_peak_rss` uses stdlib `resource` where available.

`memory_mb.tracemalloc_peak` uses stdlib `tracemalloc` and reports Python allocation tracking, not total native memory. It does not include all memory used by native extensions.

CUDA and MPS fields are optional:

- `memory_mb.cuda_peak_allocated`
- `memory_mb.cuda_peak_reserved`
- `memory_mb.mps_current_allocated`

These fields are collected only when `torch` is already installed and the backend is available. Bridge-core must not install `torch` for profiling.

## Timing Metrics

`StageTimer` records wall-clock seconds using `time.perf_counter`.

Common timing stages:

- `total`
- `decode`
- `selector`
- `src_positions`
- `patch_extract`
- `pack`
- `processor`
- `model_forward`
- `generate`
- `eval`

## Saving Profiles

Use `write_profile_json(record, path)` for single-run `profile.json`.

Use `append_profile_jsonl(record, path)` for multi-run `profile.jsonl`.

Profile outputs should go under:

- `artifacts/profiles/`
- per-run `out/` directories
- the corresponding artifact directory when a smoke script also produces `stats.json`

## Summarizing Profiles

Use the no-pandas summary script:

```bash
python scripts/profile_summary.py artifacts/profiles/profile.json
python scripts/profile_summary.py artifacts/profiles/*.jsonl
```

The table includes:

- `run_id`
- `track`
- `policy`
- total time
- selected token count
- Project A compression ratios
- Project B compression ratios
- peak RSS
- score when present
