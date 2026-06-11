# Pre-Worktree Blocker Audit

Date: `2026-06-11T07:03:29Z`

This is a local guidance report. It may be committed locally, but it must be excluded from any later public branch.

## Repository State

- Branch: `feature/gaze-ov-bridge-local`
- Latest commit: `2b5e44499c88c6aee1116487a1a456cb01098caf`
- Short HEAD: `2b5e444 Verify synthetic smoke tests after blocker resolution`
- Initial `git status --short`: clean
- Current host: `Darwin mrcui-MacBookAir.local 25.4.0 ... arm64`
- Official target remains Linux.

Recent history:

```text
2b5e444 Verify synthetic smoke tests after blocker resolution
8bb4123 Update compatibility probes after resolving download blockers
76ab762 Record Hugging Face weight download status
5eaf501 Check Linux system dependencies for codec workflow
dcb5ba9 Resolve external source and AutoGaze repo blockers
c3098c4 Add Hugging Face download utilities
cc4f37d Record post-step-11 blocker audit
631177f Add isolated environment compatibility probes
a7bbfed Record external source repository snapshot
df5f437 Add external source repository plan
dae08a6 Add Project B OV direct synthetic smoke profiling
7e06e44 Implement Project B OV direct utilities
b42d474 Add Project A codec synthetic smoke profiling
6c59b80 Implement Project A codec-compatible selector utilities
a7934fe Add profiling schema and utilities
168b90f Add Linux uv bridge-core environment scripts
3ff05af Add dependency compatibility audit plan
9b9c69f Add local Codex guidance for gaze-ov-bridge
35b40d0 Initialize VTC with gaze-ov-bridge skeleton
```

## Completed Steps

- Public VTC skeleton and `projects/gaze-ov-bridge` package skeleton.
- Local guidance files committed separately from public skeleton/source commits.
- Dependency compatibility audit.
- Linux-first uv bridge-core environment.
- HF cache/download tooling and token-safe download scripts.
- Profiling schema and pure-Python profiling utilities.
- Project A pure-Python 112-anchor selector, codec `src_positions`, stats, artifact helpers, and synthetic smoke.
- Project B pure-Python OV-direct positions, patch extraction, pack planning, stats, and synthetic smoke.
- External source repository plan and source-only snapshots.
- AutoGaze HF repo verification: `nvidia/AutoGaze` is the selected first weight-download candidate.
- System dependency checker for `ffmpeg`, `git`, and `curl`.
- Compatibility probe scaffolding and best-effort no-sync probe results.
- Synthetic smoke status after blocker-resolution attempts.

## Current Directory Summary

Environment scaffolds:

```text
envs/autogaze/
envs/bridge-core/
envs/hf-tools/
envs/llava-ov2/
envs/lmms-eval/
envs/mps-probe/
envs/ov-encoder/
```

External source paths present:

```text
external/AutoGaze
external/LLaVA-OneVision-2
external/LLaVA-OneVision-2-8B-Instruct-code
external/OneVision-Encoder
external/lmms-eval
```

External source commit/revision evidence:

- AutoGaze: `ba48d0f94ac2929d6fe3ee4380dc893aa6eed0ab` on `main`
- LLaVA-OneVision-2: `ee337788824119dc1fed9fa5e461867ed01057c0` on `main`
- lmms-eval: `3997a60cb8e79d9341ac1e4a286f0bb739bcc779` on `llava-onevision2`
- LLaVA-OV2 HF custom code: `5a75eaf7d3cd73de6f85e637e45b420f46857d2e`
- OneVision-Encoder HF custom code: recorded in public snapshot as `9908b86a6c651379df4a0b0a7ecfccc6afcd544e`

Weight/cache directories:

```text
weights/checkpoints/AutoGaze
weights/checkpoints/LLaVA-OneVision-2-8B-Instruct
weights/checkpoints/onevision-encoder-large
weights/hf_home
weights/hf_home/hub
```

Checkpoint payload status:

```text
0B weights/checkpoints/AutoGaze
0B weights/checkpoints/LLaVA-OneVision-2-8B-Instruct
0B weights/checkpoints/onevision-encoder-large
```

Compatibility artifacts present:

```text
artifacts/compat/autogaze_probe.json
artifacts/compat/llava_ov2_probe.json
artifacts/compat/lmms_eval_probe.json
artifacts/compat/mps_probe_probe.json
artifacts/compat/ov_encoder_probe.json
artifacts/profiles/compat_autogaze.json
artifacts/profiles/compat_llava_ov2.json
artifacts/profiles/compat_lmms_eval.json
artifacts/profiles/compat_mps_probe.json
artifacts/profiles/compat_ov_encoder.json
```

Synthetic smoke outputs present under ignored `out/` directories:

```text
projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/
projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/
```

## Missing Or Incomplete Steps

- Model weights have not been downloaded.
- HF token/authenticated access has not been configured in the current shell.
- Linux `ffmpeg` is not verified; local macOS host has no `ffmpeg` on `PATH`.
- Model-specific envs have not been fully synced with heavy dependencies.
- Model-specific import probes remain partial because `torch`, `transformers`, model/video deps, and benchmark deps are absent from unsynced envs.
- Runtime `flash_attn` versus SDPA/eager fallback behavior is still unknown.
- CUDA availability is not verified on the official Linux target.
- MPS remains optional and unverified for model paths.
- No real AutoGaze, OV-Encoder, LLaVA-OV2, or `lmms-eval` inference/evaluation has been run.

## Lightweight Check Results

Passing commands:

```bash
bash -n scripts/*.sh
```

Exit code: `0`

```bash
source scripts/env_weights.sh
```

Output snippet:

```text
VTC_ROOT=/Users/mrc/Documents/VTC
HF_HOME=/Users/mrc/Documents/VTC/weights/hf_home
HF_HUB_CACHE=/Users/mrc/Documents/VTC/weights/hf_home/hub
CHECKPOINTS=/Users/mrc/Documents/VTC/weights/checkpoints
```

```bash
command -v uv
command -v git
command -v curl
```

Output snippets:

```text
/Users/mrc/.local/bin/uv
/usr/bin/git
/usr/bin/curl
```

```bash
cd envs/bridge-core
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run pytest ../../projects/gaze-ov-bridge/tests
```

Result:

```text
35 passed in 0.51s
```

```bash
cd envs/bridge-core
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run python -m compileall ../../projects/gaze-ov-bridge/src
```

Result:

```text
Listing '../../projects/gaze-ov-bridge/src'...
Listing '../../projects/gaze-ov-bridge/src/gaze_ov_bridge'...
Listing '../../projects/gaze-ov-bridge/src/gaze_ov_bridge.egg-info'...
```

Diagnostic fallback command:

```bash
cd envs/bridge-core
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run python -m py_compile ../../scripts/*.py
```

Exit code: `0`

Failing or unresolved commands:

```bash
python -m py_compile scripts/*.py
```

Exit code: `127`

Error snippet:

```text
zsh:1: command not found: python
```

```bash
command -v ffmpeg
```

Exit code: `1`

Error snippet: no output.

```bash
ffmpeg -version
```

Exit code: `127`

Error snippet:

```text
zsh:1: command not found: ffmpeg
```

## Blocker Register

### B01: HF token/authentication is not configured

- Classification: `hf_auth_required`
- Severity: `critical`
- Evidence: `weights_snapshot.md` records `HF_TOKEN` not set and CLI login unauthenticated under `HF_HOME`.
- Impact: Private or gated repos cannot be downloaded. Public repos may still hit rate limits.
- Proposed fix: Source `scripts/env_weights.sh`, then authenticate through `HF_TOKEN` in the shell or `uv run hf auth login` inside `envs/hf-tools`.
- Needs HF token: yes, for private/gated repos or rate-limit-safe large downloads
- Needs gated repo approval: maybe, only if a future payload download is gated
- Needs external clone: no
- Needs weight download: no for auth check
- Needs Linux system package: no
- Needs CUDA: no
- Needs MPS optional test: no
- Needs code change: no

### B02: Model weights are absent

- Classification: `hf_download_failure`
- Severity: `critical`
- Evidence: all checkpoint directories are `0B`; weight downloads were skipped because `VTC_ALLOW_WEIGHT_DOWNLOAD` was not set.
- Impact: Real AutoGaze generation, OV-Encoder forward, LLaVA-OV2 generation, and `lmms-eval` cannot run.
- Proposed fix: Run explicit download commands only after user approval and disk/auth preflight.
- Needs HF token: maybe
- Needs gated repo approval: maybe
- Needs external clone: no
- Needs weight download: yes
- Needs Linux system package: no
- Needs CUDA: no for download, maybe later for runtime
- Needs MPS optional test: no
- Needs code change: no

### B03: Linux ffmpeg/system dependency is unverified

- Classification: `ffmpeg_missing`, `system_dependency_missing`
- Severity: `high_project_a`
- Evidence: local `command -v ffmpeg` exits `1`; `ffmpeg -version` exits `127`.
- Impact: LLaVA-OV2 codec backend and real video preprocessing remain blocked.
- Proposed fix: Install/verify `ffmpeg` on the official Linux target and rerun `bash scripts/check_system_deps.sh`.
- Needs HF token: no
- Needs gated repo approval: no
- Needs external clone: no
- Needs weight download: no
- Needs Linux system package: yes
- Needs CUDA: no
- Needs MPS optional test: no
- Needs code change: no

### B04: Model env dependency resolution is incomplete

- Classification: `dependency_resolution_failure`
- Severity: `high_project_a`, `high_project_b`
- Evidence: compatibility probes used `uv run --no-sync`; model envs lack `uv.lock` files except bridge-core and hf-tools.
- Impact: Import/runtime readiness is unknown for AutoGaze, OV-Encoder, LLaVA-OV2, and `lmms-eval`.
- Proposed fix: Lock/sync each model env separately, starting with import-only probes and no model downloads.
- Needs HF token: no for dependency resolution
- Needs gated repo approval: no for dependency resolution
- Needs external clone: no
- Needs weight download: no
- Needs Linux system package: maybe for video libs/ffmpeg
- Needs CUDA: maybe for envs that require `flash_attn`
- Needs MPS optional test: optional
- Needs code change: maybe, if env pins need adjustment

### B05: Attention fallback is unknown at runtime

- Classification: `attention_fallback_unknown`, `flash_attn_blocker`
- Severity: `high_project_a`, `high_project_b`
- Evidence: source shows SDPA/eager indicators for LLaVA-OV2 and OneVision-Encoder, but runtime probes have not confirmed fallback. AutoGaze declares `flash_attn`; `lmms-eval` adapter defaults to `flash_attention_2`.
- Impact: CPU/MPS/non-CUDA probes may fail, and some paths may be Linux/CUDA-only.
- Proposed fix: After isolated env sync, run import/runtime probes for `attn_implementation="eager"` or `sdpa`; classify mandatory FlashAttention paths as Linux/CUDA-only.
- Needs HF token: no
- Needs gated repo approval: no
- Needs external clone: no
- Needs weight download: no for import/fallback probe
- Needs Linux system package: no
- Needs CUDA: maybe, if fallback fails
- Needs MPS optional test: optional
- Needs code change: maybe, if explicit fallback configuration is required

### B06: LLaVA-OV2 processor/backend import is not proven

- Classification: `processor_import_blocker`
- Severity: `high_project_a`
- Evidence: `llava_ov2` probe reports missing `torch`, `transformers`, `huggingface_hub`, `codec_video_prep`, `cv2`, `decord`, and `qwen_vl_utils`.
- Impact: Project A model/backend work cannot start beyond artifact-contract integration.
- Proposed fix: Sync/probe `envs/llava-ov2` in isolation, verify processor imports and codec paths without generation.
- Needs HF token: no for local import
- Needs gated repo approval: no for local import
- Needs external clone: no
- Needs weight download: no
- Needs Linux system package: yes for codec/ffmpeg tests
- Needs CUDA: maybe
- Needs MPS optional test: optional
- Needs code change: maybe, if import paths need wrapper fixes

### B07: OV-Encoder import is not proven

- Classification: `ov_encoder_import_blocker`
- Severity: `high_project_b`
- Evidence: `ov_encoder` probe reports missing `torch` and `transformers`; OneVision-Encoder modules fail import without them.
- Impact: Project B model-forward work cannot start beyond artifact-contract integration.
- Proposed fix: Sync/probe `envs/ov-encoder`, target `transformers==4.57.3`, and verify `patch_positions` with no weights or inference first.
- Needs HF token: no for import
- Needs gated repo approval: no for import
- Needs external clone: no
- Needs weight download: no
- Needs Linux system package: no
- Needs CUDA: maybe
- Needs MPS optional test: optional
- Needs code change: maybe, if local source import wiring needs adjustment

### B08: AutoGaze actual generation is not runnable yet

- Classification: `dependency_resolution_failure`, `flash_attn_blocker`
- Severity: `high_project_a`, `high_project_b`
- Evidence: AutoGaze source imports are visible, but runtime dependencies such as `torch`, `transformers`, `flash_attn`, `timm`, `hydra`, `av`, and `imageio` are absent in the unsynced probe.
- Impact: Real `gazing_pos` and `if_padded_gazing` artifacts cannot be produced yet.
- Proposed fix: Sync/probe `envs/autogaze` on Linux, verify FlashAttention policy, then download `nvidia/AutoGaze` weights only when explicitly allowed.
- Needs HF token: maybe
- Needs gated repo approval: maybe
- Needs external clone: no
- Needs weight download: yes for actual generation
- Needs Linux system package: maybe for video decode
- Needs CUDA: likely if `flash_attn` is mandatory
- Needs MPS optional test: optional
- Needs code change: maybe, if artifact export wrapper is needed

### B09: lmms-eval is deferred

- Classification: `lmms_eval_blocker`
- Severity: `medium`
- Evidence: `lmms_eval` source is importable, but the LLaVA-OV2 adapter import fails because benchmark deps such as `loguru`, `torch`, and `transformers` are absent. No benchmark was run.
- Impact: Full answer-level benchmark cannot start.
- Proposed fix: Keep `envs/lmms-eval` isolated and probe only after Project A generation path works.
- Needs HF token: later, for model weights
- Needs gated repo approval: maybe
- Needs external clone: no
- Needs weight download: later
- Needs Linux system package: yes for video/codec benchmark
- Needs CUDA: likely for full benchmark
- Needs MPS optional test: no
- Needs code change: likely later for profiling hooks

### B10: MPS probe remains optional and incomplete

- Classification: `mps_optional_blocker`
- Severity: `low`
- Evidence: optional MPS probe ran on Darwin, but `torch`, `numpy`, and `PIL` were absent in the unsynced optional env.
- Impact: No official Linux blocker. MPS claims cannot be made for model paths.
- Proposed fix: Only sync `envs/mps-probe` if a lightweight Mac diagnostic is useful.
- Needs HF token: no
- Needs gated repo approval: no
- Needs external clone: no
- Needs weight download: no
- Needs Linux system package: no
- Needs CUDA: no
- Needs MPS optional test: yes
- Needs code change: no

### B11: Bare `python` is unavailable on this host

- Classification: `script_failure`
- Severity: `low`
- Evidence: `python -m py_compile scripts/*.py` fails with `zsh:1: command not found: python`.
- Impact: Some generic docs/commands fail locally; project `uv run python` works.
- Proposed fix: Prefer `uv run python` inside a configured env, or document local shell requirements.
- Needs HF token: no
- Needs gated repo approval: no
- Needs external clone: no
- Needs weight download: no
- Needs Linux system package: no
- Needs CUDA: no
- Needs MPS optional test: no
- Needs code change: docs cleanup only if desired

## Non-Blockers Confirmed

- Classification: `smoke_test_failure`
- Status: no active blocker. Bridge-core tests pass: `35 passed in 0.51s`.
- Classification: `profiling_schema_blocker`
- Status: no active blocker. Project A and Project B smoke profiles are present and documented in `docs/public/synthetic_smoke_status.md`.
- Classification: `source_repo_missing`
- Status: no active blocker for the currently planned source audit. Expected source paths are present, including `external/OneVision-Encoder`.
- Classification: `autogaze_repo_unverified`
- Status: no active blocker. `nvidia/AutoGaze` is verified as the first download candidate. `bfshi/AutoGaze` remains stale/private/unavailable unless the user provides new evidence.

## Recommended Execution Order

1. Keep Project A and Project B pure-Python bridge worktrees unblocked; use the synthetic smoke artifacts and profiling schema as gates.
2. Verify Linux `ffmpeg` on the actual Linux target with `bash scripts/check_system_deps.sh`.
3. Authenticate Hugging Face safely if private/gated access or rate-limit-safe large downloads are needed.
4. Recheck disk space before any weight download.
5. Download weights only after explicit approval and target flags:
   - `nvidia/AutoGaze`
   - `lmms-lab-encoder/onevision-encoder-large`
   - `lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct`
6. Sync/probe `envs/ov-encoder` without inference; verify `transformers==4.57.3`, imports, and SDPA/eager feasibility.
7. Sync/probe `envs/llava-ov2` without generation; verify processor/custom-code imports, codec dependency imports, and attention fallback.
8. Sync/probe `envs/autogaze` on Linux; classify whether `flash_attn` is mandatory.
9. Defer `envs/lmms-eval` until the LLaVA-OV2 runtime path is working and profiled.
10. Run optional `envs/mps-probe` only as a best-effort Mac diagnostic.
