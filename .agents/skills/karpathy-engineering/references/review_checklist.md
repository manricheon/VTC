# Review Checklist

Use this for code review, worktree handoff, blocker resolution review, and model-integration review.

## Setup / Env

- `uv` is used.
- `bridge-core` stays free of model dependencies.
- Model dependencies remain isolated in their `envs/*` environment.
- `external/`, `weights/`, `artifacts/`, and `out/` are not staged.
- Linux is treated as official; MPS is best-effort only.

## Project A

- `decoded_entries -> selected_112_blocks -> src_positions` is explicit.
- 112 anchor policy is preserved.
- 224 acts as fine evidence.
- 56 and 28 remain priors by default.
- Hard union is explicit ablation only.
- `src_positions` are integer `[frame_id, native_h, native_w]`.

## Project B

- One AutoGaze selected token maps to one OV token.
- Coarse tokens are not expanded into native-grid union.
- Fractional `patch_positions` are explicit.
- Patch extraction and pack metadata preserve token order.

## Profiling

- Smoke paths write `stats.json` and `profile.json`.
- Token counts are present.
- Compression ratios are present.
- Timing stages are present.
- Memory fields are present where possible.
- Missing CUDA/MPS metrics are explicit, not hidden.

## External / HF / Weights

- Source-only repos live under `external/`.
- HF cache/checkpoints live under `weights/`.
- Tokens are never printed.
- Gated/auth failures name the repo and next action.
- No weight files are staged.

## Worktree Readiness

- `bash scripts/pre_worktree_gate.sh` has been run.
- Project A smoke passes if Project A is in scope.
- Project B smoke passes if Project B is in scope.
- Blockers are documented with exact commands/errors.
- Worktree changes do not mix local guidance and public code unless explicitly asked.
