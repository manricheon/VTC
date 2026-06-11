# Simplicity Review

Date:

Commit:

Scope:

Tests run:

- 

Simplicity findings:

- 

Refactor candidates:

- 

Blocker risks:

- 

Next actions:

- 

## Review Entry: 2026-06-11T12:58:59Z

Commit: `d473d07ba700eac07d3734984c7948b72dd12f79`

Scope: final simplicity and worktree readiness review after `Simplify bridge code for collaborative development`.

Tests run:

- `git status --short`: clean before writing this local review entry.
- `bash scripts/simplicity_gate.sh || true`: completed.
- `bash scripts/pre_worktree_gate.sh || true`: completed with `READY_FOR_WORKTREE=1`.
- `cd envs/bridge-core && uv run pytest ../../projects/gaze-ov-bridge/tests`: 37 passed.
- `uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py`: passed.
- `uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py`: passed.
- `uv run python ../../scripts/profile_summary.py ...`: completed for Project A and Project B smoke profiles.

Smoke status:

- Project A codec synthetic smoke passed.
  - valid AutoGaze tokens: 5
  - selected 112 blocks: 2
  - raw patch tokens: 8
  - LLM visual tokens: 2
  - dense raw/visual compression ratios: 0.015625 / 0.015625
  - no-hard-union default confirmed.
- Project B OV-direct synthetic smoke passed.
  - direct tokens: 5
  - tokens by scale: `{28: 2, 56: 1, 112: 1, 224: 1}`
  - candidate/dense compression ratios: 0.007353 / 0.009766
  - no-native-union default confirmed.

Profile status:

- Project A profile exists at `projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/profile.json`.
- Project B profile exists at `projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/profile.json`.
- Profile summary prints both smoke profiles with timing, compression, selected/direct token count, and peak RSS.

Remaining complexity concerns:

- Model environment setup remains intentionally separated and not fully synced for heavy envs.
- Attention fallback is documented but not proven by real import/runtime probes.
- Codec/backend path still depends on ffmpeg availability on the target machine.
- Real model profiling must preserve the current shared profile schema instead of adding ad hoc fields.

Blockers:

- `ffmpeg` is missing on this Mac probe environment; Linux target must install or verify it before codec/backend runtime work.
- `envs/autogaze`, `envs/ov-encoder`, `envs/llava-ov2`, `envs/lmms-eval`, and `envs/mps-probe` have no lockfiles in the current status output.
- `HF_TOKEN` is not set in this shell; gated/private HF access would require user authentication.
- CUDA and flash-attn runtime readiness remain unverified and should be treated as Linux/CUDA-specific until probes prove otherwise.

Worktree recommendation:

- `READY_FOR_WORKTREE=1` for bridge-core worktree tasks because Project A/B pure-Python tests, synthetic smokes, and profiles pass.
- Start with Project A LLaVA-OV2 codec-compatible integration planning/worktree, but keep any real processor/backend work gated on ffmpeg, model-env import probes, and attention fallback verification.
- Project B OV-direct worktree can start for artifact/geometry/pack integration, but real OV-Encoder forward should wait for the isolated `ov-encoder` env probe.
- lmms-eval worktree should wait until LLaVA-OV2 env import/probe and a minimal runner path are verified.
