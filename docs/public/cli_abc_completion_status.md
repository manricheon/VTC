# CLI A/B/C Completion Status

Date: 2026-06-11

## Current Branch

- Branch: `feature/gaze-ov-bridge-local`
- Head before this status document: `9aab60c Add lmms-eval autogaze profiling plan`

## Commits Created

- `edd815e Plan CLI sequential A/B/C tasks`
- `06e234a Add Project A LLaVA codec boundary validation`
- `7e9b0ae Add Project B OV direct boundary validation`
- `9aab60c Add lmms-eval autogaze profiling plan`

## Task A Status

Status: complete for artifact-boundary validation.

Added:

- `projects/gaze-ov-bridge/src/gaze_ov_bridge/project_a_llava_boundary.py`
- `projects/gaze-ov-bridge/scripts/smoke_project_a_llava_boundary.py`
- `projects/gaze-ov-bridge/tests/test_project_a_llava_boundary.py`
- `docs/public/project_a_llava_boundary.md`

Validated:

- `selected_blocks.json` and `src_positions.npy` load.
- `src_positions` shape is `[N, 3]`.
- rows are integer `[frame_idx, native_h, native_w]`.
- native coordinates are within `0..15`.
- `N == selected_112_blocks * 4`.
- native 2x2 ordering is enforced.
- source-only LLaVA-OV2 codec boundary inspection finds codec processor paths.

Not done:

- No LLaVA-OV2 import.
- No generation.
- No lmms-eval execution.

## Task B Status

Status: complete for artifact-boundary validation.

Added:

- `projects/gaze-ov-bridge/src/gaze_ov_bridge/project_b_ov_boundary.py`
- `projects/gaze-ov-bridge/scripts/smoke_project_b_ov_boundary.py`
- `projects/gaze-ov-bridge/tests/test_project_b_ov_boundary.py`
- `docs/public/project_b_ov_boundary.md`

Validated:

- `patches.npy`, `patch_positions.npy`, and `pack_plan.json` load.
- `patches` contain 14x14 patch tensors.
- `patch_positions` shape is `[K, 3]`.
- each decoded AutoGaze entry maps to exactly one OV token.
- coarse tokens are not expanded into native-grid union.
- fractional OV positions match the shared formula.
- pack-plan token order is stable and padding slots are excluded from metadata.
- source-only OneVision-Encoder inspection finds `patch_positions`, `visible_indices`,
  3D RoPE, and attention implementation indicators.

Not done:

- No OneVision-Encoder import.
- No real OV forward.

## Task C Status

Status: complete for planning and guarded runner skeleton.

Added:

- `docs/public/lmms_eval_plan.md`
- `scripts/run_lmms_eval_autogaze_limit1.sh`
- `scripts/collect_lmms_eval_profiles.py`
- `projects/gaze-ov-bridge/tests/test_collect_lmms_eval_profiles.py`

Validated:

- lmms-eval source branch is `llava-onevision2`.
- wrapper path found: `external/lmms-eval/lmms_eval/models/chat/llava_onevision2.py`.
- frames launcher found: `external/lmms-eval/examples/llava_onevision2_repro/run_frames.sh`.
- codec launcher found: `external/lmms-eval/examples/llava_onevision2_repro/run_codec.sh`.
- limit-one runner is dry-run by default and requires `RUN_LMMS_EVAL=1` to execute.
- profile collector summarizes synthetic JSONL without pandas.

Not done:

- No full lmms-eval benchmark.
- No dataset download.
- No model generation.

## Verification Run

Final gate commands run:

- `bash scripts/simplicity_gate.sh || true`
- `bash scripts/pre_worktree_gate.sh || true`
- `uv run pytest ../../projects/gaze-ov-bridge/tests`
- `uv run python -m compileall ../../projects/gaze-ov-bridge/src`
- `uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py`
- `uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py`
- `uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_llava_boundary.py`
- `uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_boundary.py`

Observed result:

- `READY_FOR_WORKTREE=1`
- bridge-core tests: `56 passed`
- compileall: passed
- Project A codec synthetic smoke: passed
- Project B OV-direct synthetic smoke: passed
- Project A LLaVA boundary smoke: passed
- Project B OV boundary smoke: passed

The host has no bare `python` command, so Python checks were run through the
uv-managed bridge-core interpreter.

## Smoke And Profile Status

Project A synthetic:

- valid AutoGaze tokens: `5`
- selected 112 blocks: `2`
- raw patch tokens: `8`
- LLM visual tokens: `2`
- dense raw ratio: `0.015625`
- dense visual ratio: `0.015625`

Project B synthetic:

- direct tokens: `5`
- tokens by scale: `{'28': 2, '56': 1, '112': 1, '224': 1}`
- candidate ratio: `0.007353`
- dense native ratio: `0.009766`

Boundary smokes:

- Project A boundary source probe status: `present`
- Project B boundary source probe status: `present`

Generated smoke outputs remain under `projects/gaze-ov-bridge/out/` and are not
committed.

## Remaining Blockers

- Linux runtime gate still needs to be run on the official Linux target.
- Heavy model environments still need full sync/probe.
- `flash_attn`/CUDA runtime readiness is not verified.
- SDPA/eager fallback is source-indicated but not runtime-proven.
- MPS remains optional and best-effort.
- Real LLaVA-OV2 generation is deferred.
- Real OV-Encoder forward is deferred.
- Full lmms-eval benchmark is deferred.
- Dataset availability for lmms-eval tasks is not verified.

## Next CLI Step

Run the model-environment import probes on the official Linux machine, then
attempt one import-only LLaVA-OV2 processor probe before any generation:

```bash
VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh
bash scripts/run_compat_probes.sh
```
