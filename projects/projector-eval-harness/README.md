# projector-eval-harness

Guarded VTC harness for comparing LLaVA-1.5 projector/token-compression methods
through `lmms-eval`.

The v1 scope is source audit, dry-run runners, profile summaries, and
`lmms-eval` plugin wrappers for:

- `vtc_fourier_llava15`
- `vtc_divt_llava15`

The package does not download weights, datasets, or modify upstream source
repositories.

See:

- `docs/public/projector_eval_harness.md`
- `docs/public/projector_eval_benchmark_guide.md`
- `docs/public/projector_eval_report_template.md`
