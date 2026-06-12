# Projector Eval Benchmark Guide

This guide runs the Fourier-Compressor and DiVT projector comparison through
`lmms-eval` without modifying upstream source trees.

Run commands from the VTC repo root unless noted otherwise.

## Target Runtime

Use Linux/CUDA for real benchmark runs. macOS/MPS is only for light source,
matrix, and dry-run checks.

Required local inputs:

- `external/lmms-eval`
- `external/Fourier-Compressor`
- `external/DiVT`
- Fourier-compatible LLaVA-1.5 checkpoint under `weights/checkpoints/llava-v1.5-7b`
- DiVT-compatible checkpoint under `weights/checkpoints/llava-v1.5-divt-0.65-7b`
- Dataset access/cache for the selected `lmms-eval` tasks

The harness never downloads weights or datasets by default.

## One-Time Checks

Verify the third-party source snapshots:

```bash
bash scripts/audit_projector_sources.sh
```

Sync the eval environments on the Linux/CUDA machine:

```bash
cd envs/fourier-llava15-eval
uv sync

cd ../divt-llava15-eval
uv sync
```

The Fourier environment still needs an importable official LLaVA package at
runtime. The env skeleton wires the Fourier repo and `lmms-eval`; it does not
vendor LLaVA automatically.

## Dry-Run

Print the planned default limit-one MME commands:

```bash
bash scripts/run_projector_eval_limit1.sh
```

Print the full benchmark matrix:

```bash
cd envs/bridge-core
PYTHONPATH=../../projects/projector-eval-harness/src \
  uv run python -m vtc_projector_eval.matrix --preset smoke --projector-model all --limit 1
```

## Limit-One Smoke

Run both projectors on one example per task:

```bash
for task in mme pope textvqa_val_lite vqav2_val_lite scienceqa_img mmbench_en_dev_lite gqa_lite; do
  RUN_PROJECTOR_EVAL=1 \
  PROJECTOR_MODEL=all \
  TASK="${task}" \
  LIMIT=1 \
  RUN_ID="smoke_${task}" \
    bash scripts/run_projector_eval_limit1.sh
done
```

Profile rows are appended to:

```text
artifacts/profiles/projector_eval_<RUN_ID>.jsonl
```

Task outputs and logs are written under:

```text
artifacts/profiles/projector_eval_<RUN_ID>_<projector>_<task>/
```

## Full Runs

After limit-one succeeds, run the same tasks without `lmms-eval --limit`:

```bash
for task in mme pope textvqa_val vqav2_val scienceqa_img mmbench_en_dev gqa mmvet; do
  RUN_PROJECTOR_EVAL=1 \
  PROJECTOR_MODEL=all \
  TASK="${task}" \
  LIMIT=none \
  RUN_ID="full_${task}" \
    bash scripts/run_projector_eval_limit1.sh
done
```

Useful overrides:

- `PROJECTOR_MODEL=fourier|divt|all`
- `FOURIER_CKPT=/abs/path/to/llava-v1.5-7b`
- `DIVT_CKPT=/abs/path/to/llava-v1.5-divt-0.65-7b`
- `DEVICE_MAP=auto`
- `NPROC=1`
- `PORT=29840`
- `FOURIER_RESERVE=12`
- `DIVT_THRESHOLD=0.65`

## Summaries

Summarize one or more JSONL profile files:

```bash
bash scripts/summarize_projector_eval_profiles.sh \
  artifacts/profiles/projector_eval_smoke_mme.jsonl
```

Write a Markdown benchmark report:

```bash
bash scripts/write_projector_eval_report.sh \
  --run-id smoke_2026_06_12 \
  --preset smoke \
  --output-md docs/public/projector_eval_current_report.md \
  artifacts/profiles/projector_eval_smoke_*.jsonl
```

For full runs, use `--preset full` and pass the corresponding
`projector_eval_full_*.jsonl` files:

```bash
bash scripts/write_projector_eval_report.sh \
  --run-id full_2026_06_12 \
  --preset full \
  --limit none \
  --output-md docs/public/projector_eval_current_report.md \
  artifacts/profiles/projector_eval_full_*.jsonl
```

## Reporting Checklist

Before treating a run as comparable:

- Source audit passes for Fourier-Compressor and DiVT.
- Both projectors use the intended LLaVA-1.5 base/checkpoint family.
- Both projectors run the same `lmms-eval` task name, split, limit, batch size,
  and prompt/evaluation settings.
- Each task has a saved `run.log`.
- The report records any task failures, OOMs, retries, or backend changes.
- Generated artifacts stay under `artifacts/`; checkpoints stay under `weights/`.
