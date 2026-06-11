# lmms-eval Autogaze Codec Plan

This is a planning and runner-skeleton step only. It does not run the full
benchmark and does not run LLaVA-OV2 generation by default.

## Source Paths Found

lmms-eval source:

- `external/lmms-eval`
- branch: `llava-onevision2`
- observed commit: `3997a60 feat: add tuned online codec fallback path`

LLaVA-OV2 wrapper and launchers:

- `external/lmms-eval/lmms_eval/models/chat/llava_onevision2.py`
  - registered model: `llava_onevision2`
  - `video_backend` accepts `frames` or `codec`
  - `codec_target_canvas`, `codec_group_size`, and `codec_images_per_group`
    are model args
  - `generate_until` tracks e2e latency and calls `log_metrics`
  - codec path supports online tuned codec and optional
    `LLAVA_CODEC_OFFLINE_ROOT`
- `external/lmms-eval/examples/llava_onevision2_repro/run_frames.sh`
  - frames backend launcher
  - uses `--model llava_onevision2`
  - model args include `video_backend=frames`
- `external/lmms-eval/examples/llava_onevision2_repro/run_codec.sh`
  - codec backend launcher
  - model args include `video_backend=codec` and `codec_target_canvas=${TC}`
  - writes to `out/<task>_codec_*`
- `external/lmms-eval/README.md`
  - documents frames and codec reproduction settings
  - notes codec runtime needs `codec-video-prep-legacy-exact` and ffmpeg

Relevant LLaVA-OneVision-2 source:

- `external/LLaVA-OneVision-2/transformers_impl/llavaonevision2/processing_llava_onevision2.py`
- `external/LLaVA-OneVision-2/transformers_impl/llavaonevision2/modeling_llava_onevision2.py`
- `external/LLaVA-OneVision-2/tools/frame_extraction/core/run_cut_frames.py`

## Planned Baselines

Run in this order after runtime blockers are cleared:

- `frames`
- `codec`
- `autogaze_codec_anchor112`
- `autogaze_codec_112_only`
- `autogaze_codec_112_plus_224`
- `autogaze_codec_112_plus_224_plus_56_rep`
- `hard_union_ablation`

The `hard_union_ablation` backend must remain explicit. It is not the default
Project A policy.

## Execution Plan

1. First `--limit 1` smoke.
2. Then a small subset with saved samples and per-sample profiles.
3. Then full benchmark after the sample-level outputs are understood.

The guarded skeleton command is:

```bash
bash scripts/run_lmms_eval_autogaze_limit1.sh
```

It prints the planned command and exits without running. To execute the limit-one
smoke after blockers are cleared:

```bash
RUN_LMMS_EVAL=1 TASK=JumpScore TC=128 TS=2 bash scripts/run_lmms_eval_autogaze_limit1.sh
```

## Runtime Blockers

- Linux runtime verification.
- ffmpeg installed and available.
- `envs/lmms-eval` sync with heavy dependencies.
- LLaVA-OV2 attention backend verification.
- `flash_attn`/CUDA readiness or a proven SDPA/eager runtime fallback.
- LLaVA-OV2 checkpoint files.
- Dataset availability for the selected task.
- `codec-video-prep-legacy-exact` for codec backend.

## Project A Artifact Input

Future autogaze codec backends should consume Project A artifacts:

- `selected_blocks.json`
- `src_positions.npy`
- `profile.json`

The lmms-eval runtime must not import AutoGaze directly. AutoGaze outputs should
be serialized to JSON/NPY artifacts and converted into codec-compatible
`src_positions`.

## Per-Sample Profiling Fields

Every lmms-eval sample profile should include:

- `sample_id`
- `task_name`
- `backend`
- `policy_name`
- `score` or correctness if available
- `preprocess_time`
- `processor_time`
- `model_time`
- `generation_time`
- `total_time`
- `raw_patch_tokens`
- `llm_visual_tokens`
- compression ratios
- peak memory when available

Profiles should be JSONL so partial benchmark runs remain inspectable.

Output locations:

- `artifacts/profiles/lmms_eval_<run_id>.jsonl`
- `artifacts/profiles/lmms_eval_<run_id>_summary.json`

The summary helper is:

```bash
python scripts/collect_lmms_eval_profiles.py artifacts/profiles/lmms_eval_<run_id>.jsonl
```

It works without pandas and prints a compact per-backend summary.
