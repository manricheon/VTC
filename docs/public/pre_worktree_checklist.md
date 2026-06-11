# Pre-Worktree Readiness Checklist

Status date: `2026-06-11T07:03:29Z`

This checklist is the shareable gate before starting Codex app worktrees. It records what is ready for parallel Project A/B bridge work and what still blocks model-runtime work.

No model inference was run for this checklist. No weights were downloaded.

## Setup Scripts

Required scripts are present:

- [x] `scripts/install_uv_linux.sh`
- [x] `scripts/bootstrap_bridge_core.sh`
- [x] `scripts/env_weights.sh`
- [x] `scripts/check_linux_env.py`
- [x] `scripts/check_system_deps.sh`
- [x] `scripts/profile_summary.py`
- [x] `scripts/run_compat_probes.sh`
- [x] `scripts/hf_auth_check.py`
- [x] `scripts/hf_download_plan.py`
- [x] `scripts/hf_download_snapshot.py`
- [x] `scripts/hf_download_code_only.sh`
- [x] `scripts/hf_download_weights.sh`
- [x] `projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py`
- [x] `projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py`

Latest lightweight script checks:

- `bash -n scripts/*.sh`: pass
- `uv run python -m py_compile ../../scripts/*.py` from `envs/bridge-core`: pass
- Bare `python -m py_compile scripts/*.py`: unavailable on the current local shell because `python` is not on `PATH`; use `uv run python`.

## External Sources

Source-only external paths are present and ignored by git:

| Target | Path | Status | Notes |
| --- | --- | --- | --- |
| AutoGaze | `external/AutoGaze` | present | Source commit recorded in `docs/public/external_snapshot.md`. |
| LLaVA-OneVision-2 | `external/LLaVA-OneVision-2` | present | Source commit recorded in `docs/public/external_snapshot.md`. |
| lmms-eval | `external/lmms-eval` | present | `llava-onevision2` branch commit recorded in `docs/public/external_snapshot.md`. |
| LLaVA-OV2 HF custom code | `external/LLaVA-OneVision-2-8B-Instruct-code` | present | Code/config/text snapshot only. |
| OneVision-Encoder HF custom code | `external/OneVision-Encoder` | present | Code/config/text snapshot only. |

Source-only confirmation:

- No `.safetensors`, `.bin`, `.pt`, `.pth`, `.gguf`, or `.onnx` payload files were found under `external/`.
- `external/` must remain uncommitted.

## Hugging Face Code And Weights

HF cache policy:

- Source `scripts/env_weights.sh` before any HF operation.
- `HF_HOME` and `HF_HUB_CACHE` must point under `weights/`.
- `weights/` must remain uncommitted.

Code snapshots:

- [x] LLaVA-OV2 custom code snapshot is present under `external/`.
- [x] OneVision-Encoder custom code snapshot is present under `external/`.

Weight checkpoints:

| Target | Repo id | Local path | Status |
| --- | --- | --- | --- |
| AutoGaze | `nvidia/AutoGaze` | `weights/checkpoints/AutoGaze` | skipped, directory exists with no payload files |
| OneVision-Encoder | `lmms-lab-encoder/onevision-encoder-large` | `weights/checkpoints/onevision-encoder-large` | skipped, directory exists with no payload files |
| LLaVA-OV2 | `lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct` | `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct` | skipped, directory exists with no payload files |

AutoGaze repo decision:

- `nvidia/AutoGaze` is the first weight-download candidate.
- `bfshi/AutoGaze` remains stale/private/unavailable unless new evidence or access is provided.

Before any weight download:

- Recheck disk space.
- Authenticate safely if needed.
- Set `VTC_ALLOW_WEIGHT_DOWNLOAD=1`.
- Set exactly the target download flags.
- Do not place weights outside `weights/`.

## System Dependencies

Current `ffmpeg` status:

- `ffmpeg` is not available on the current local PATH.
- Linux `ffmpeg` status remains unverified.
- Codec/backend tests remain blocked until `ffmpeg` is installed and verified on the Linux target.

System checker:

```bash
bash scripts/check_system_deps.sh
```

Failing gate form:

```bash
REQUIRED_SYSTEM_DEPS=1 bash scripts/check_system_deps.sh
```

Manual install commands are recorded in `docs/public/system_dependencies.md`.

## Bridge-Core Gate

Latest bridge-core checks:

- `uv run pytest ../../projects/gaze-ov-bridge/tests`: `35 passed`
- `uv run python -m compileall ../../projects/gaze-ov-bridge/src`: pass

Bridge-core remains isolated from:

- `torch`
- `transformers`
- `flash_attn`
- AutoGaze runtime imports
- LLaVA-OV2 runtime imports
- OneVision-Encoder runtime imports
- `lmms-eval`
- model weights

## Project A Synthetic Smoke

Status: ready for artifact-contract worktree.

Track: `project_a_codec`

Policy: `anchor112_default`

Output directory:

```text
projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/
```

Current metrics:

- AutoGaze valid tokens: `5`
- Selected 112 blocks: `2`
- Project A raw patch tokens: `8`
- Project A LLM visual tokens: `2`
- Dense raw compression ratio: `0.015625`
- Dense visual compression ratio: `0.015625`
- No-hard-union default confirmed.

Ready artifacts:

- `decoded_entries.json`
- `selected_blocks.json`
- `src_positions.npy`
- `stats.json`
- `profile.json`

Still blocked for real LLaVA-OV2 runtime:

- LLaVA-OV2 weights absent.
- `envs/llava-ov2` not synced with heavy deps.
- `ffmpeg` missing/unverified.
- Attention fallback not confirmed.
- CUDA not verified.

## Project B Synthetic Smoke

Status: ready for artifact-contract worktree.

Track: `project_b_ov_direct`

Policy: `direct_multiscale_no_union`

Output directory:

```text
projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/
```

Current metrics:

- OV-direct tokens: `5`
- Tokens by scale: `28=2`, `56=1`, `112=1`, `224=1`
- Project B vs AutoGaze candidates ratio: `0.007352941176470588`
- Project B vs dense native ratio: `0.009765625`
- No-native-union confirmed.

Ready artifacts:

- `decoded_entries.json`
- `patch_positions.npy`
- `patches.npy`
- `pack_plan.json`
- `stats.json`
- `profile.json`

Still blocked for real OV-Encoder runtime:

- OneVision-Encoder weights absent.
- `envs/ov-encoder` not synced with heavy deps.
- `torch`/`transformers` import path not confirmed.
- Attention fallback not confirmed.
- CUDA not verified.

## Profiling Output

Ready:

- Project A smoke writes `stats.json` and `profile.json`.
- Project B smoke writes `stats.json` and `profile.json`.
- Compatibility probes wrote profile-like JSON files under `artifacts/profiles/`.
- `scripts/profile_summary.py` can summarize smoke and compatibility profile JSON files.

Limitations:

- bridge-core memory profiling is stdlib/NumPy only.
- CUDA/MPS memory metrics remain null until `torch` is installed in model-specific envs.
- Real model profiles still need processor/model/generate/eval timing fields.

## Compatibility Probe Status

| Env | Status | Main blocker | Next action |
| --- | --- | --- | --- |
| `bridge-core` | pass | none for pure Python bridge work | Continue Project A/B bridge work. |
| `autogaze` | partial | heavy deps and weights absent; `flash_attn` policy unknown | Sync/probe on Linux before real generation. |
| `ov-encoder` | partial | `torch`/`transformers` absent; weights absent | Sync/probe `envs/ov-encoder`; test SDPA/eager path. |
| `llava-ov2` | partial | runtime deps, weights, and `ffmpeg` absent | Verify `ffmpeg`, sync/probe, then download weights when approved. |
| `lmms-eval` | partial/deferred | benchmark deps absent; model paths not validated | Keep last. |
| `mps-probe` | optional/deferred | optional env unsynced; torch absent | Run only if a local MPS diagnostic is useful. |

## Criteria For Starting Codex App Worktrees

Project A bridge artifact-contract worktree can start when:

- [x] bridge-core tests pass.
- [x] Project A synthetic smoke passes.
- [x] Project A profile/stat artifacts exist.
- [x] External LLaVA-OV2 source and custom code are present.
- [x] Worktree scope excludes real model generation unless weights/env/ffmpeg are resolved.

Project B bridge artifact-contract worktree can start when:

- [x] bridge-core tests pass.
- [x] Project B synthetic smoke passes.
- [x] Project B profile/stat artifacts exist.
- [x] OneVision-Encoder custom code is present for source inspection.
- [x] Worktree scope excludes real encoder forward unless weights/env/attention backend are resolved.

Model-runtime worktrees can start only after:

- [ ] Required weights are downloaded under `weights/`.
- [ ] Linux `ffmpeg` is installed/verified for codec workflows.
- [ ] The matching isolated env is synced and import-probed.
- [ ] Attention backend behavior is classified.
- [ ] CUDA requirements are known for any path that requires `flash_attn`.

Recommended start order:

1. Project A artifact-contract worktree.
2. Project B artifact-contract worktree.
3. `envs/ov-encoder` import/fallback probe worktree.
4. `envs/llava-ov2` import/codec dependency probe worktree.
5. `envs/autogaze` generation environment worktree.
6. `envs/lmms-eval` benchmark/profiling worktree.
