# User Guide Status

Date: 2026-06-12

Branch: `feature/gaze-ov-bridge-local`

Commit checked: `e51dc41`

## Current Readiness

- `ready_for_boundary_usage`: yes
- `not_ready_for_real_runtime`: yes
- `benchmark_prepared_but_not_executed`: yes

The repository is ready for a new developer or agent to run the current pure-Python bridge tests, Project A/B synthetic smokes, Project A/B boundary smokes, profile summaries, and benchmark readiness checks.

The repository is not claiming full runtime readiness. Real AutoGaze inference, real LLaVA-OV2 generation, real OV-Encoder forward, and full lmms-eval execution remain deferred until the model-specific environments are synced and checked on the official Linux/CUDA target.

## Documents Present

- Root overview: `README.md`
- Subproject overview: `projects/gaze-ov-bridge/README.md`
- Setup: `docs/public/quickstart.md`
- Project A usage: `docs/public/usage_project_a.md`
- Project B usage: `docs/public/usage_project_b.md`
- Architecture: `docs/public/architecture.md`
- Profiling: `docs/public/profiling.md`
- Benchmark preparation: `docs/public/benchmarking.md`
- Benchmark readiness: `docs/public/benchmark_readiness.md`
- Troubleshooting: `docs/public/troubleshooting.md`
- Agent handoff: `docs/public/agent_handoff.md`
- Current status: `docs/public/current_status.md`
- User-facing readiness: `docs/public/user_facing_readiness.md`
- Completion audit: `docs/public/completion_audit.md`

## Scripts Present

- `scripts/setup_bridge_core.sh`
- `scripts/vtc_doctor.sh`
- `scripts/pre_worktree_gate.sh`
- `scripts/run_all_smokes.sh`
- `scripts/run_project_a_examples.sh`
- `scripts/run_project_b_examples.sh`
- `scripts/run_profile_summaries.sh`
- `scripts/check_benchmark_readiness.sh`
- `scripts/run_lmms_eval_autogaze_limit1.sh`
- `scripts/profile_summary.py`
- `scripts/compare_profiles.py`
- `scripts/collect_lmms_eval_profiles.py`

## Commands Tested

These commands were run on the current Mac probe host using uv-managed Python where needed:

```bash
bash scripts/vtc_doctor.sh
UV_CACHE_DIR=/private/tmp/vtc-uv-cache bash scripts/pre_worktree_gate.sh
UV_CACHE_DIR=/private/tmp/vtc-uv-cache bash scripts/run_all_smokes.sh
UV_CACHE_DIR=/private/tmp/vtc-uv-cache bash scripts/run_profile_summaries.sh
bash scripts/check_benchmark_readiness.sh
cd envs/bridge-core
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run pytest ../../projects/gaze-ov-bridge/tests
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run python -m compileall ../../projects/gaze-ov-bridge/src
```

Results:

- Bridge-core tests: `56 passed`
- Project A codec synthetic smoke: passed
- Project A LLaVA boundary smoke: passed
- Project B OV-direct synthetic smoke: passed
- Project B OV boundary smoke: passed
- Profile summary over all four smoke profiles: passed
- Benchmark readiness check: `READY_FOR_BENCHMARK=1` for local skeleton/readiness inputs

Note: the host has `python3` and uv-managed Python, but no bare `python` command. Project scripts should continue to use `uv run python`.

## Remaining Blockers

- Official Linux runtime gate still needs to be run on Linux.
- CUDA runtime readiness is not proven.
- `flash_attn` runtime readiness is not proven.
- SDPA/eager fallback is source-indicated but not runtime-proven.
- Heavy model environments need final sync/import probes before real runtime.
- Real LLaVA-OV2 generation is not run yet.
- Real OV-Encoder forward is not run yet.
- Full lmms-eval benchmark is not run yet.
- Dataset availability for lmms-eval is not verified here.

## Recommended Next Stage

1. Linux runtime gate.
2. Project A real LLaVA-OV2 generation smoke.
3. Project B real OV-Encoder forward smoke.
4. lmms-eval `--limit 1` smoke.
5. Small benchmark subset.
6. Full benchmark.

## Commands Users Should Run Next

On a Linux target:

```bash
source scripts/env_weights.sh
bash scripts/vtc_doctor.sh
bash scripts/check_system_deps.sh
bash scripts/setup_bridge_core.sh
bash scripts/run_all_smokes.sh
bash scripts/run_profile_summaries.sh
bash scripts/check_benchmark_readiness.sh
```

Only after model environments and runtime blockers are resolved:

```bash
RUN_LMMS_EVAL=1 TASK=JumpScore TC=128 TS=2 bash scripts/run_lmms_eval_autogaze_limit1.sh
```

## Docs Another Agent Should Read First

1. `docs/public/agent_handoff.md`
2. `docs/public/current_status.md`
3. `docs/public/quickstart.md`
4. `docs/public/architecture.md`
5. `docs/public/usage_project_a.md`
6. `docs/public/usage_project_b.md`
7. `docs/public/benchmarking.md`
8. `docs/public/troubleshooting.md`
9. `docs/public/blocker_resolution_status.md`

## Boundary vs Runtime Statement

Project A and Project B are boundary-ready. They validate artifact contracts, token accounting, compression ratios, and smoke profiling without importing model stacks or running generation/forward passes.

The repository is not yet runtime-ready for real model execution or benchmark scoring until Linux/CUDA, attention backend, model env sync, and dataset/runtime checks are completed.
