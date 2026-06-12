# Projector Eval Harness

This branch adds a guarded LLaVA-1.5 projector comparison harness for
Fourier-Compressor and DiVT.

## Scope

- Compare `vtc_fourier_llava15` and `vtc_divt_llava15` through `lmms-eval`.
- Keep upstream source repositories in `external/` unmodified.
- Keep heavy model dependencies out of `envs/bridge-core`.
- Do not download weights or datasets by default.

Future VTC projectors can be added as new `lmms-eval` plugin models in
`projects/projector-eval-harness/src/vtc_projector_eval/models`.

## External Source Snapshots

Expected source snapshots:

- `external/Fourier-Compressor`
  - remote: `https://github.com/whyisverysmart/Fourier-Compressor.git`
  - branch: `master`
  - expected commit: `b846f44c5c189370a94e1ec71a7dcef5ccb36d55`
- `external/DiVT`
  - remote: `https://github.com/LeeHyun98/DiVT.git`
  - branch: `main`
  - expected commit: `5ebbb162d5808d8ad3efc2514cc990487ac9296a`

Audit:

```bash
bash scripts/audit_projector_sources.sh
```

## Runners

Dry-run the default limit-one MME commands:

```bash
bash scripts/run_projector_eval_limit1.sh
```

Detailed Linux/CUDA benchmark workflow and reporting docs:

- [Projector Eval Benchmark Guide](projector_eval_benchmark_guide.md)
- [Projector Eval Report Template](projector_eval_report_template.md)
- [Current Projector Eval Report](projector_eval_current_report.md)

Run after Linux/CUDA, env sync, checkpoints, and datasets are ready:

```bash
RUN_PROJECTOR_EVAL=1 PROJECTOR_MODEL=all TASK=mme LIMIT=1 \
  bash scripts/run_projector_eval_limit1.sh
```

For full task execution, set `LIMIT=none` to omit `lmms-eval --limit`:

```bash
RUN_PROJECTOR_EVAL=1 PROJECTOR_MODEL=all TASK=mme LIMIT=none \
  bash scripts/run_projector_eval_limit1.sh
```

When running for real, wrappers append generation-stage records to:

```text
artifacts/profiles/projector_eval_<RUN_ID>.jsonl
```

Useful overrides:

- `PROJECTOR_MODEL=all|fourier|divt`
- `TASK=mme`
- `LIMIT=1|none`
- `FOURIER_CKPT=weights/checkpoints/llava-v1.5-7b`
- `DIVT_CKPT=weights/checkpoints/llava-v1.5-divt-0.65-7b`
- `FOURIER_RESERVE=12`
- `DIVT_THRESHOLD=0.65`
- `RUN_ID=limit1_mme`

## Presets

The Python matrix helper defines:

- smoke: `mme,pope,textvqa_val_lite,vqav2_val_lite,scienceqa_img,mmbench_en_dev_lite,gqa_lite`
- full: `mme,pope,textvqa_val,vqav2_val,scienceqa_img,mmbench_en_dev,gqa,mmvet`

Generate a JSON matrix:

```bash
cd envs/bridge-core
PYTHONPATH=../../projects/projector-eval-harness/src \
  uv run python -m vtc_projector_eval.matrix --preset smoke --projector-model all --limit 1
```

Summarize profiles:

```bash
bash scripts/summarize_projector_eval_profiles.sh artifacts/profiles/projector_eval_<run_id>.jsonl
```

Write a Markdown report:

```bash
bash scripts/write_projector_eval_report.sh \
  --run-id <run_id> \
  --preset smoke \
  --limit 1 \
  --output-md docs/public/projector_eval_current_report.md \
  artifacts/profiles/projector_eval_<run_id>.jsonl
```

## Runtime Blockers

The harness is intentionally guarded. Real benchmark execution still requires:

- Linux/CUDA runtime.
- `envs/fourier-llava15-eval` and/or `envs/divt-llava15-eval` synced.
- LLaVA-1.5 compatible checkpoints under `weights/`.
- Dataset availability for selected `lmms-eval` tasks.
- Attention/backend compatibility verified for the selected environment.

The Fourier environment also needs an importable official LLaVA package. The
env skeleton installs Fourier-Compressor and `lmms-eval`; it does not clone or
vendor official LLaVA automatically.
