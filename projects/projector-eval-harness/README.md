# projector-eval-harness

`projector-eval-harness` is the VTC subproject for comparing LLaVA-1.5
projector/token-compression methods through guarded `lmms-eval` wrappers.

The package is boundary-ready for source audit, benchmark matrix construction,
report generation, and dry-run command construction. Heavy model dependencies,
datasets, and checkpoint payloads are intentionally excluded from bridge-core.

## Priorities

The first comparison pair is:

- `vtc_fourier_llava15`
- `vtc_divt_llava15`

Future VTC projector variants should be added as additional `lmms-eval` plugin
models that share the same matrix, report, and smoke/reporting contracts.

## Bridge-Core Tests

From the VTC repository root:

```bash
bash scripts/setup_bridge_core.sh
```

This syncs the pure-Python bridge-core environment and runs both
`gaze-ov-bridge` and `projector-eval-harness` tests. It does not download
weights, sync heavy model environments, access datasets, or run real model
inference.

## Environment Isolation

- `envs/bridge-core` is for source audit, matrix/report generation, synthetic
  smoke, and CPU-safe tests.
- `envs/fourier-llava15-eval` is for the Fourier/LLaVA-1.5 runtime path.
- `envs/divt-llava15-eval` is for the DiVT/LLaVA-1.5 runtime path.

## Current Usage

Safe projector examples:

```bash
bash scripts/run_projector_eval_examples.sh
```

This runs source audit, a synthetic projector smoke, and a guarded `lmms-eval`
dry-run. It does not run real benchmark execution.

Default limit-one benchmark dry-run:

```bash
bash scripts/run_projector_eval_limit1.sh
```

Markdown benchmark report generation:

```bash
bash scripts/write_projector_eval_report.sh \
  --run-id current \
  --preset smoke \
  --limit 1 \
  --output-md docs/public/projector_eval_current_report.md
```

## Boundary vs Runtime

The harness currently validates:

- upstream source snapshots for Fourier-Compressor and DiVT,
- checkpoint asset mapping and blocker reporting,
- `lmms-eval` plugin model registration metadata,
- benchmark matrix and report generation,
- synthetic smoke output under `projects/projector-eval-harness/out/`.

The harness is not yet runtime-ready for real benchmark execution. Real runs
still require Linux/CUDA, synced model envs, checkpoint payloads under
`weights/checkpoints/`, dataset availability, and runtime import/backend
verification.

See:

- `docs/public/projector_eval_assets.md`
- `docs/public/projector_eval_harness.md`
- `docs/public/projector_eval_benchmark_guide.md`
- `docs/public/projector_eval_report_template.md`
