# Projector Eval Benchmark Report Template

Use this template for a completed smoke or full projector benchmark run.

## Run Metadata

- run_id:
- created_at_utc:
- machine:
- os:
- gpu:
- cuda:
- python:
- torch:
- lmms-eval commit:
- VTC commit:

## Scope

- projector models:
- preset: `smoke` or `full`
- tasks:
- limit: `1`, sample count, or `none`
- batch size:
- decoding/generation settings:

## Source Snapshots

| Source | Branch | Commit | Local modifications | Notes |
| --- | --- | --- | --- | --- |
| Fourier-Compressor |  |  |  |  |
| DiVT |  |  |  |  |
| lmms-eval |  |  |  |  |

## Checkpoints

| Model | Checkpoint path | Base model | Checksum or revision | Notes |
| --- | --- | --- | --- | --- |
| Fourier/LLaVA-1.5 |  |  |  |  |
| DiVT |  |  |  |  |

## Benchmark Matrix

| Model | Task | Split/config | Limit | Output directory |
| --- | --- | --- | ---: | --- |
| `vtc_fourier_llava15` |  |  |  |  |
| `vtc_divt_llava15` |  |  |  |  |

## Results

| Task | Fourier score | DiVT score | Delta | Fourier time | DiVT time | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| mme |  |  |  |  |  |  |
| pope |  |  |  |  |  |  |
| textvqa_val |  |  |  |  |  |  |
| vqav2_val |  |  |  |  |  |  |
| scienceqa_img |  |  |  |  |  |  |
| mmbench_en_dev |  |  |  |  |  |  |
| gqa |  |  |  |  |  |  |
| mmvet |  |  |  |  |  |  |

## Runtime Profile Summary

| Model task | Count | Mean total time | Mean model time | Mean visual tokens | Mean visual ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
|  |  |  |  |  |  |

## Failures And Deviations

- failed tasks:
- OOMs:
- retries:
- backend changes:
- dataset/cache issues:

## Reproduction Commands

```bash
bash scripts/audit_projector_sources.sh
```

```bash
RUN_PROJECTOR_EVAL=1 PROJECTOR_MODEL=all TASK=<task> LIMIT=<limit> \
  RUN_ID=<run_id> bash scripts/run_projector_eval_limit1.sh
```

```bash
bash scripts/write_projector_eval_report.sh \
  --run-id <run_id> \
  --preset <smoke|full> \
  --limit <limit|none> \
  --output-md docs/public/projector_eval_current_report.md \
  artifacts/profiles/projector_eval_<run_id>.jsonl
```

## Interpretation

- main finding:
- quality tradeoff:
- runtime/token tradeoff:
- next run:
