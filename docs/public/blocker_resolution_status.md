# Blocker Resolution Status

Status date: `2026-06-11T07:03:29Z`

No model weights were downloaded for this update. No model inference was run, no heavy model dependencies were installed, and no push was performed.

Status values used below:

- `resolved`
- `partially_resolved`
- `still_blocked`
- `needs_hf_token`
- `needs_gated_access`
- `needs_ffmpeg`
- `needs_cuda`
- `needs_model_env_probe`
- `deferred`

## Status Table

| Blocker | Status | Current evidence | Next action |
| --- | --- | --- | --- |
| Bridge-core tests and compile gate | `resolved` | `uv run pytest ../../projects/gaze-ov-bridge/tests` reports `35 passed`; `compileall` passes for `projects/gaze-ov-bridge/src`. | Keep as the required gate before source or model-runtime changes. |
| Project A synthetic smoke | `resolved` | `docs/public/synthetic_smoke_status.md` records passing `project_a_codec` smoke with `5` valid AutoGaze tokens, `2` selected 112 blocks, `8` raw patch tokens, and no-hard-union confirmation. | Project A artifact-contract work can start without real model generation. |
| Project B synthetic smoke | `resolved` | `docs/public/synthetic_smoke_status.md` records passing `project_b_ov_direct` smoke with `5` direct tokens and no-native-union confirmation. | Project B artifact-contract work can start without real encoder forward. |
| Profiling schema and smoke profiles | `resolved` | Project A and Project B smokes write `stats.json` and `profile.json`; `profile_summary.py` parses generated profiles. | Reuse the same schema for model-specific probes and later real integrations. |
| External GitHub source repos | `resolved` | `external/AutoGaze`, `external/LLaVA-OneVision-2`, and `external/lmms-eval` are present; commits are recorded in `docs/public/external_snapshot.md`. | Keep `external/` uncommitted and refresh snapshots only by explicit task. |
| LLaVA-OV2 HF custom code | `resolved` | Code/config/text snapshot exists at `external/LLaVA-OneVision-2-8B-Instruct-code`; revision is recorded in `docs/public/external_snapshot.md`; no model payloads under `external/`. | Use for processor/backend source inspection and no-weight import probes. |
| OneVision-Encoder HF custom code | `resolved` | Code/config/text snapshot exists at `external/OneVision-Encoder`; revision is recorded in `docs/public/external_snapshot.md`; no model payloads under `external/`. | Use for Project B source inspection and no-weight import probes. |
| AutoGaze HF repo verification | `resolved` | `nvidia/AutoGaze` is public, ungated in metadata, `model_type=autogaze`, and has `config.json`, `preprocessor_config.json`, and `model.safetensors`. | Use `VTC_AUTOGAZE_REPO=nvidia/AutoGaze` for the first approved AutoGaze weight-download attempt. |
| `bfshi/AutoGaze` ambiguity | `partially_resolved` | Source quick-start references it, but public metadata/listing returned unavailable without a token. Public README points to `nvidia/AutoGaze`. | Treat as stale/private/renamed unless the user provides access or new evidence. |
| HF token/authentication | `needs_hf_token` | Existing docs record no `HF_TOKEN` and no authenticated CLI state under `HF_HOME`. Public metadata/code access worked; large downloads may still need auth for rate limits or private/gated repos. | Authenticate through `HF_TOKEN` in the shell or `uv run hf auth login` under `envs/hf-tools`; never commit tokens. |
| Potential gated/private repo access | `needs_gated_access` | No active gated failure was hit because weight downloads were intentionally skipped, but private/gated access remains possible for future payload downloads. | If a download reports gated/private access, accept/request access for that exact repo, then rerun with safe auth. |
| Weight downloads | `still_blocked` | `weights/checkpoints/AutoGaze`, `weights/checkpoints/onevision-encoder-large`, and `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct` exist but contain no payload files. | Download only after explicit approval, disk preflight, and target flags. Commands are in `docs/public/weights_snapshot.md`. |
| Linux ffmpeg/system dependency | `needs_ffmpeg` | Current local PATH has no `ffmpeg`; Linux target status remains unverified. Codec backend tests require `ffmpeg` on PATH. | Install/verify `ffmpeg` on Linux and run `bash scripts/check_system_deps.sh`. |
| Model-specific env import probes | `needs_model_env_probe` | Current compatibility probes were `uv run --no-sync`; heavy deps were not installed, so model runtime imports remain unavailable. | Sync/probe each env separately, starting with `envs/ov-encoder` and `envs/llava-ov2`; keep `lmms-eval` last. |
| AutoGaze runtime env | `needs_model_env_probe` | AutoGaze source is present, but runtime deps such as `torch`, `transformers~=4.51`, `flash_attn`, video libs, and weights are absent. | Sync/probe `envs/autogaze` on Linux; classify FlashAttention policy before real generation. |
| LLaVA-OV2 processor/backend env | `needs_model_env_probe` | HF custom code is present, but `torch`, `transformers`, video deps, codec deps, weights, and `ffmpeg` are absent/unverified. | Verify `ffmpeg`, sync/probe `envs/llava-ov2`, test processor/backend imports without generation, then download weights when approved. |
| OV-Encoder runtime env | `needs_model_env_probe` | HF custom code is present, but `torch`, `transformers`, weights, and attention fallback behavior are unverified. | Sync/probe `envs/ov-encoder` with the intended Transformers version and explicit SDPA/eager checks. |
| `flash_attn` requirements | `needs_cuda` | bridge-core does not require `flash_attn`. AutoGaze declares it; LLaVA-OV2 and OneVision source show fallback indicators, but runtime fallback is unverified; `lmms-eval` adapter defaults to `flash_attention_2`. | Confirm `sdpa`/`eager` behavior after isolated env sync. Classify mandatory FlashAttention paths as Linux/CUDA-only. |
| CUDA availability | `needs_cuda` | No CUDA runtime verification has been performed on the official Linux target. | Verify only on the Linux CUDA machine after dependencies and weights are available. |
| MPS optional probes | `deferred` | Optional MPS probe is partial and torch is absent; MPS is not an official target. | Run only if a local Mac/MPS diagnostic is useful; do not treat as Linux support. |
| lmms-eval benchmark | `deferred` | Source adapter exists and has timing/token hooks, but benchmark deps, model runtimes, weights, and `ffmpeg` are not ready. | Keep isolated in `envs/lmms-eval`; start after Project A model path works. |

## Worktree Readiness Decision

Project A bridge artifact-contract worktree:

- Status: ready.
- Scope allowed: bridge-core artifact contract, profile/stat validation, LLaVA-OV2 processor boundary planning without generation.
- Scope blocked: real LLaVA-OV2 generation, codec backend execution, weight-backed tests.

Project B bridge artifact-contract worktree:

- Status: ready.
- Scope allowed: bridge-core artifact contract, OV-direct patch/position contract, pack metadata, profile/stat validation.
- Scope blocked: real OV-Encoder forward, weight-backed tests.

Model-runtime worktrees:

- Status: blocked until the matching env is synced/probed and required weights/system deps are available.

## Recommended Next Order

1. Start Project A artifact-contract worktree.
2. Start Project B artifact-contract worktree.
3. Verify/install Linux `ffmpeg`.
4. Sync/probe `envs/ov-encoder` without inference.
5. Sync/probe `envs/llava-ov2` without generation.
6. Sync/probe `envs/autogaze` on Linux.
7. Download weights only after explicit approval and disk/auth preflight.
8. Defer `envs/lmms-eval` until Project A generation path is ready.
