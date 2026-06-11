# Blocker Resolution Status

Status date: `2026-06-11T14:11:43Z`

No push was performed. No model inference was run. `external/`, `weights/`, `artifacts/`, and `projects/gaze-ov-bridge/out/` remain uncommitted.

## Status Table

| Blocker | Status | Evidence | Next action |
| --- | --- | --- | --- |
| Bridge-core tests and compile gate | `resolved` | `pytest` reports 37 passed; `compileall` passes. | Keep as required gate. |
| Project A synthetic smoke/profile | `resolved` | Project A smoke passes with 2 selected 112 blocks, 8 raw patch tokens, and profile output. | Start Project A artifact-contract worktree. |
| Project B synthetic smoke/profile | `resolved` | Project B smoke passes with 5 direct tokens and profile output. | Start Project B artifact-contract worktree. |
| Profiling schema and summary | `resolved` | `profile_summary.py` parses both smoke profiles. | Reuse for model probes. |
| External source repos | `resolved` | `audit_external_sources.sh` finds all expected external paths. | Keep `external/` ignored. |
| AutoGaze HF repo verification | `resolved` | `nvidia/AutoGaze` is the selected AutoGaze repo; payload exists locally. | Use this repo for future refreshes. |
| HF token/access | `partially_resolved` | `HF_TOKEN` is not set; current payloads are present in public-only mode. | Authenticate only if future gated/private access is needed. |
| Weight directories | `resolved` | `check_hf_assets.sh` reports payloads for AutoGaze, OneVision-Encoder, and LLaVA-OV2. | Do not commit `weights/`. |
| Model env lockfiles dirty tree | `resolved` | `docs/public/model_env_lock_status.md` records valid TOML, clean secret/path scans, matching env metadata, and passing `uv lock --check` for all five model env lockfiles. | Commit model env lockfiles as public reproducibility artifacts; regenerate later on Linux if runtime probes require it. |
| Linux ffmpeg/system dependency | `needs_ffmpeg` | `check_system_deps.sh` reports `ffmpeg` missing on current host; Linux target unverified. | Install/verify on Linux before codec/backend runtime work. |
| Model-specific env import probes | `needs_model_env_probe` | no heavy sync; no-sync probes are partial. | Run `VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh`. |
| AutoGaze runtime env | `needs_model_env_probe` | source and weights present; runtime deps not synced. | Sync/probe isolated `envs/autogaze`. |
| LLaVA-OV2 processor/backend env | `needs_model_env_probe` | source and weights present; runtime deps and `ffmpeg` absent/unverified. | Sync/probe isolated `envs/llava-ov2`. |
| OV-Encoder runtime env | `needs_model_env_probe` | source and weights present; runtime deps/fallback unverified. | Sync/probe isolated `envs/ov-encoder`. |
| `flash_attn` requirements | `needs_cuda` | no-sync probes show `flash_attn` absent; source suggests fallbacks but runtime is unverified. | Verify `sdpa`/`eager` or classify as Linux/CUDA-only. |
| CUDA availability | `needs_cuda` | no CUDA target checked in this pass. | Verify on official Linux CUDA machine. |
| MPS optional probe | `deferred` | no-sync MPS probe ran, but torch is absent; MPS is not official. | Run only as best-effort local diagnostic. |
| lmms-eval benchmark | `deferred` | source adapter exists; benchmark env not synced and Project A runtime path not verified. | Defer until LLaVA-OV2 runtime path works. |
| Pre-worktree automation | `resolved` | doctor, system deps, HF asset check, external audit, bridge setup, model-env wrapper, HF wrapper, compat probes, and gate scripts exist. | Use scripts before worktree handoff. |

## Worktree Readiness

Project A worktree: ready for artifact-contract and integration-boundary work; blocked for real generation until runtime blockers are resolved.

Project B worktree: ready for artifact-contract and integration-boundary work; blocked for real encoder forward until runtime blockers are resolved.

Worktree C / lmms-eval: not ready for benchmark work; start only after Project A model-runtime path works.

Final gate: `READY_FOR_WORKTREE=1`.
