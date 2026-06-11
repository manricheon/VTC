---
name: karpathy-engineering
description: Use this skill for all VTC/gaze-ov-bridge development, debugging, review, refactoring, and worktree handoff. It enforces simple code, small experiments, explicit contracts, profiling, reproducible checks, and collaboration-friendly changes.
---

# Karpathy Engineering

## Core Rule

Use this skill for all VTC and `projects/gaze-ov-bridge` work. This is not only a review skill. It applies to new code, refactors, blocker resolution, environment scripts, external/HF asset setup, profiling, worktree handoff, and model integration.

The default style is simple, explicit, measurable, and easy to hand off.

## When Working

1. Start from the existing contract and the smallest useful change.
2. Prefer plain functions over classes.
3. Add a class only when stateful behavior is truly necessary.
4. Avoid deep abstraction layers.
5. Add helper functions only when they remove real duplication or clarify a stable contract.
6. Keep functions short enough to read without jumping around.
7. Prefer explicit dictionaries, or dataclasses only when they clarify a data contract.
8. Avoid clever code.
9. Avoid silent fallback.
10. Avoid broad exception handling unless the exact error is reported.
11. If a dependency, repo, model path, backend, or device is not verified, say so.

## Commit Hygiene

- Keep public/shared files separate from local/private guidance.
- Do not mix local guidance commits with public code commits.
- Do not commit `external/`, `weights/`, `artifacts/`, or `projects/gaze-ov-bridge/out/`.
- Worktree tasks must not change guidance files unless explicitly asked.

## Verification

Every nontrivial change must have one of:

- `pytest`
- synthetic smoke
- profile output
- documented blocker with exact command/error evidence

Every smoke or model path must report token counts and profiling fields. Do not claim model readiness from source inspection alone.

Read checklists when relevant:

- New work or feature implementation: `references/simple_code_checklist.md`
- Reviews and handoffs: `references/review_checklist.md`
- Refactors: `references/refactor_checklist.md`

## Project A Rules

AutoGaze -> LLaVA-OV2 codec-compatible is priority 1.

Keep this contract explicit:

```text
decoded_entries -> selected_112_blocks -> src_positions -> LLaVA-compatible payload
```

Rules:

- `112` scale is the canonical anchor.
- `224` scale is fine evidence for the containing 112 block.
- `56` scale is region prior.
- `28` scale is frame/global prior.
- Hard union exists only as an explicit ablation.
- `src_positions` are integer `[frame_id, native_h, native_w]`.

Always profile:

- selected blocks
- raw patch tokens
- LLM visual tokens
- dense comparison
- compression ratio
- latency
- memory when possible

## Project B Rules

AutoGaze -> OV-Encoder direct is priority 2.

Rules:

- Preserve one AutoGaze selected token as one OV token.
- Do not expand coarse tokens into native grid union.
- Keep fractional `patch_positions = [t, h, w]` explicit.
- Keep JSON/NPY artifact contracts readable and inspectable.

Always profile:

- valid AutoGaze tokens
- OV direct tokens
- dense comparison
- compression ratio
- patch extraction time
- memory when possible

## Environment Rules

Keep environments separated:

- `envs/bridge-core`
- `envs/autogaze`
- `envs/ov-encoder`
- `envs/llava-ov2`
- `envs/lmms-eval`
- `envs/mps-probe`

Do not merge model dependencies into bridge-core. Use JSON/NPY artifact exchange between envs.

Storage rules:

- HF downloads go under `weights/`.
- Third-party source goes under `external/`.
- Cross-env artifacts go under `artifacts/`.
- MPS is best-effort only; Linux remains official support.

## Worktree Rules

Worktrees may run Project A, Project B, lmms-eval, and profiling/report work in parallel.

Before starting worktrees:

```bash
bash scripts/pre_worktree_gate.sh
```

Before handoff or merge:

```bash
bash scripts/simplicity_gate.sh
```

Worktree results must be tested locally before merging.
