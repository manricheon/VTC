# Agent Handoff

This repo is ready for another agent to inspect and extend the boundary-ready
bridge code. It is not ready for real model runtime claims without the deferred
runtime probes.

## Read First

1. `README.md`
2. `docs/public/current_status.md`
3. `docs/public/quickstart.md`
4. `docs/public/architecture.md`
5. `docs/public/profiling.md`
6. `docs/public/usage_project_a.md`
7. `docs/public/usage_project_b.md`
8. `docs/public/benchmarking.md` if benchmark work is in scope

For local-only behavior, also read `AGENTS.md` when available in the working
copy.

## Suggested Roles

Claude:

- review docs and architecture
- critique plans
- simplify contracts
- look for hidden coupling and overstatement

Codex:

- implement code and tests
- run scripts and smoke checks
- maintain uv environment scripts
- produce reproducible commits

## Rules

- Do not edit the same files simultaneously across agents.
- Use worktrees for parallel implementation when possible.
- Run bridge-core tests before and after source changes.
- Keep public docs/scripts separate from local guidance commits.
- Record public blockers under `docs/public/`.
- Record sensitive or local-only notes under `docs/local/`.
- Do not commit `external/`, `weights/`, `artifacts/`, or `projects/gaze-ov-bridge/out/`.

## Core Commands

```bash
bash scripts/pre_worktree_gate.sh
cd envs/bridge-core
uv run pytest ../../projects/gaze-ov-bridge/tests
cd ../..
```

Run safe examples:

```bash
bash scripts/run_all_smokes.sh
bash scripts/run_profile_summaries.sh
```

Benchmark readiness check:

```bash
bash scripts/check_benchmark_readiness.sh
```

## Current Boundary Contracts

Project A:

```text
decoded_entries -> selected_112_blocks -> src_positions -> LLaVA-compatible payload
```

Project B:

```text
decoded_entries -> patches -> patch_positions -> pack_plan
```

Do not claim model runtime from these boundary checks alone.
