# Engineering Principles

VTC uses a simple-code, metrics-first engineering style. The goal is to make bridge logic easy to read, easy to test, and easy to hand off across isolated environments.

## Coding Style

- Prefer small functions over classes.
- Add classes only when they clarify stateful behavior.
- Avoid deep abstraction layers.
- Add helpers only when they remove meaningful duplication or clarify a stable contract.
- Keep paths, environment variables, and artifact schemas explicit.
- Avoid clever code and silent fallback.
- Report exact errors when handling failures.
- Mark unverified dependencies, model paths, and hardware assumptions as unverified.

## Testing Expectations

- Pure Python bridge logic is tested first in `envs/bridge-core`.
- Synthetic tests come before real model tests.
- Nontrivial changes need a reproducible check: pytest, smoke, profile, or documented blocker.
- Shape checks are not enough when behavior matters; tests should verify token counts, coordinates, ordering, and artifact round trips.

## Profiling Expectations

Every smoke and integration path should produce metrics for:

- wall-clock timing by stage
- token counts
- compression ratios
- memory where possible
- environment metadata
- run id and git commit when available

Bridge-core profiling uses stdlib and NumPy first. CUDA/MPS metrics are optional and collected only when the matching backend is installed and available.

## Artifact Contracts

Use explicit JSON/NPY artifacts between environments. Do not import model packages across environment boundaries.

Project A keeps the codec-compatible contract explicit:

```text
decoded_entries -> selected_112_blocks -> src_positions -> LLaVA-compatible payload
```

Project B keeps the OV-direct contract explicit:

```text
decoded_entries -> patches -> patch_positions -> pack_plan
```

## Environment Separation

Keep model stacks isolated:

- `envs/bridge-core` for pure Python bridge code
- `envs/autogaze` for AutoGaze generation
- `envs/ov-encoder` for OneVision-Encoder direct work
- `envs/llava-ov2` for LLaVA-OV2 processor/backend/generation
- `envs/lmms-eval` for benchmark work
- `envs/mps-probe` for optional Mac/MPS probes

HF checkpoints and caches live under `weights/`. Third-party source lives under `external/`. Cross-environment artifacts live under `artifacts/`.

## Collaboration Expectations

- Keep changes small enough to review.
- Keep public code and local/private guidance separate.
- Record blockers with exact commands and short error snippets.
- Do not claim runtime support from source inspection alone.
- Run the relevant gate before handoff.
