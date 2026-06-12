# Projector Eval Benchmark Report

- run_id: `current`
- created_at_utc: `2026-06-12T10:59:24Z`
- preset: `smoke`
- tasks: `mme,pope,textvqa_val_lite,vqav2_val_lite,scienceqa_img,mmbench_en_dev_lite,gqa_lite`
- limit: `1`
- profiles: `-`

## Status

Benchmark execution is blocked for real runs.

- missing checkpoint for Fourier/LLaVA-1.5: weights/checkpoints/llava-v1.5-7b
- missing checkpoint for DiVT: weights/checkpoints/llava-v1.5-divt-0.65-7b

## Source Snapshots

| Source | Status | Branch | Commit | Required files | Terms |
| --- | --- | --- | --- | --- | --- |
| Fourier-Compressor | ok | master | `b846f44c5c18` | ok | ok |
| DiVT | ok | main | `5ebbb162d580` | ok | ok |

## Benchmark Matrix

| Model | Task | Limit | Model args |
| --- | --- | ---: | --- |
| `vtc_fourier_llava15` | `mme` | 1 | `pretrained=${FOURIER_CKPT},device_map=auto,use_flash_attention_2=False,fourier_reserve=12` |
| `vtc_fourier_llava15` | `pope` | 1 | `pretrained=${FOURIER_CKPT},device_map=auto,use_flash_attention_2=False,fourier_reserve=12` |
| `vtc_fourier_llava15` | `textvqa_val_lite` | 1 | `pretrained=${FOURIER_CKPT},device_map=auto,use_flash_attention_2=False,fourier_reserve=12` |
| `vtc_fourier_llava15` | `vqav2_val_lite` | 1 | `pretrained=${FOURIER_CKPT},device_map=auto,use_flash_attention_2=False,fourier_reserve=12` |
| `vtc_fourier_llava15` | `scienceqa_img` | 1 | `pretrained=${FOURIER_CKPT},device_map=auto,use_flash_attention_2=False,fourier_reserve=12` |
| `vtc_fourier_llava15` | `mmbench_en_dev_lite` | 1 | `pretrained=${FOURIER_CKPT},device_map=auto,use_flash_attention_2=False,fourier_reserve=12` |
| `vtc_fourier_llava15` | `gqa_lite` | 1 | `pretrained=${FOURIER_CKPT},device_map=auto,use_flash_attention_2=False,fourier_reserve=12` |
| `vtc_divt_llava15` | `mme` | 1 | `pretrained=${DIVT_CKPT},device_map=auto,use_flash_attention_2=False,divt_threshold=0.65` |
| `vtc_divt_llava15` | `pope` | 1 | `pretrained=${DIVT_CKPT},device_map=auto,use_flash_attention_2=False,divt_threshold=0.65` |
| `vtc_divt_llava15` | `textvqa_val_lite` | 1 | `pretrained=${DIVT_CKPT},device_map=auto,use_flash_attention_2=False,divt_threshold=0.65` |
| `vtc_divt_llava15` | `vqav2_val_lite` | 1 | `pretrained=${DIVT_CKPT},device_map=auto,use_flash_attention_2=False,divt_threshold=0.65` |
| `vtc_divt_llava15` | `scienceqa_img` | 1 | `pretrained=${DIVT_CKPT},device_map=auto,use_flash_attention_2=False,divt_threshold=0.65` |
| `vtc_divt_llava15` | `mmbench_en_dev_lite` | 1 | `pretrained=${DIVT_CKPT},device_map=auto,use_flash_attention_2=False,divt_threshold=0.65` |
| `vtc_divt_llava15` | `gqa_lite` | 1 | `pretrained=${DIVT_CKPT},device_map=auto,use_flash_attention_2=False,divt_threshold=0.65` |

## Result Summary

No profile rows were found.

## Run Commands

Dry-run:

```bash
bash scripts/run_projector_eval_limit1.sh
```

Execution after blockers are cleared:

```bash
RUN_PROJECTOR_EVAL=1 PROJECTOR_MODEL=all TASK=mme LIMIT=1 \
  bash scripts/run_projector_eval_limit1.sh
```

Summarize profiles:

```bash
bash scripts/summarize_projector_eval_profiles.sh \
  artifacts/profiles/projector_eval_<run_id>.jsonl
```

Write report:

```bash
bash scripts/write_projector_eval_report.sh \
  --run-id current \
  --preset smoke \
  --limit 1 \
  --output-md docs/public/projector_eval_current_report.md \
  artifacts/profiles/projector_eval_<run_id>.jsonl
```

## Notes

- Upstream source trees under `external/` are not modified or committed.
- `weights/` and `artifacts/` remain local/generated storage.
- Score fields are unavailable until real `lmms-eval` task result records exist.
