# Benchmarking

Benchmark execution is not full-ready yet. The boundary/profile infrastructure
is ready, and lmms-eval integration is planned, but real benchmark runs still
require model runtime gates.

## Status

- Boundary/profile infrastructure: ready.
- lmms-eval plan and guarded `--limit 1` runner: present.
- Full benchmark runtime: not ready until blockers below are resolved.

## Planned Baselines

- `frames`
- `codec`
- `autogaze_codec_anchor112`
- `autogaze_codec_112_only`
- `autogaze_codec_112_plus_224`
- `autogaze_codec_112_plus_224_plus_56_rep`
- `hard_union_ablation`

`hard_union_ablation` must remain explicit. It is not the default Project A
policy.

## First Target

1. `--limit 1` smoke.
2. Small subset.
3. Full benchmark.

Dry-run the planned command:

```bash
bash scripts/run_lmms_eval_autogaze_limit1.sh
```

After blockers are resolved:

```bash
RUN_LMMS_EVAL=1 TASK=JumpScore TC=128 TS=2 bash scripts/run_lmms_eval_autogaze_limit1.sh
```

## Requirements

- Linux runtime.
- `ffmpeg`.
- LLaVA-OV2 model env synced and import-probed.
- LLaVA-OV2 model weights under `weights/`.
- Dataset availability for the selected task.
- Attention backend readiness.
- CUDA is recommended for default FlashAttention-oriented paths.

## Profiling Fields

Per-sample profiles should include:

- `sample_id`
- `task_name`
- `backend`
- `policy_name`
- `score` or correctness
- `preprocess_time`
- `processor_time`
- `model_time`
- `generation_time`
- `total_time`
- `raw_patch_tokens`
- `llm_visual_tokens`
- compression ratios
- peak memory

## Output Locations

- `artifacts/profiles/lmms_eval_<run_id>.jsonl`
- `artifacts/profiles/lmms_eval_<run_id>_summary.json`

Summarize:

```bash
python scripts/collect_lmms_eval_profiles.py artifacts/profiles/lmms_eval_<run_id>.jsonl
```

Compare:

```bash
python scripts/compare_profiles.py profile_a.json profile_b.json
```
