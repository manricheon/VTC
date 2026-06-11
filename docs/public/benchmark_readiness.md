# Benchmark Readiness

Date: 2026-06-12

## Current Readiness

Benchmark execution is prepared but not executed. The repo has source, weights,
boundary artifacts, and guarded scripts, but real benchmark runtime still needs
Linux/model-env/attention/dataset validation.

## Checklist

- external/lmms-eval present: yes.
- ffmpeg present on current host: yes; still verify on official Linux target.
- LLaVA-OV2 weights present: yes.
- `envs/lmms-eval` synced: not proven.
- Project A boundary ready: yes.
- autogaze codec runner skeleton exists: yes.
- profile collection exists: yes.
- profile comparison exists: yes.

## Current Command

```bash
bash scripts/check_benchmark_readiness.sh
```

The script prints `READY_FOR_BENCHMARK=1` only when local path and system checks
are present. It does not run lmms-eval and does not prove model runtime.

## Blockers

- `envs/lmms-eval` heavy runtime still needs sync/import validation.
- LLaVA-OV2 processor/model import is not runtime-proven.
- Attention backend fallback is not runtime-proven.
- Dataset availability is not verified.
- Full Linux/CUDA runtime gate remains.

## Next Action

On the official Linux target:

```bash
VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh
bash scripts/run_compat_probes.sh
bash scripts/check_benchmark_readiness.sh
```
