# Compatibility Probe Results

Probe date: `2026-06-11T06:21:15Z`

Probes were run best-effort after external source setup, system dependency checks, and the weight-download attempt. No additional weights were downloaded, no full model inference was run, and `lmms-eval` was not benchmarked.

Command:

```bash
UV_CACHE_DIR=/private/tmp/vtc-uv-cache RUN_UV_PROBES=1 RUN_OPTIONAL_MPS=1 bash scripts/run_compat_probes.sh
```

The aggregate runner used `uv run --no-sync` to avoid installing heavy model dependencies. It created empty `.venv` directories as needed, but did not sync dependency sets.

Runtime artifacts were written under:

- `artifacts/compat/*_probe.json`
- `artifacts/profiles/compat_*.json`

These artifacts are ignored by git and are not committed.

## Summary

| Env | Status | Main blockers | Weight availability | Profiling capability | Next action |
| --- | --- | --- | --- | --- | --- |
| `bridge-core` | pass | none for pure Python tests | not needed | profile summary can parse compat profiles | Continue Project A/B pure-Python work. |
| `autogaze` | partial | deps not synced; `torch`, `transformers`, `flash_attn`, video libs absent; ffmpeg absent | AutoGaze dir exists but has no payload files | process RSS and tracemalloc available; torch memory unavailable | Sync/probe `envs/autogaze` on Linux/CUDA after deciding FlashAttention policy and downloading weights. |
| `ov_encoder` | partial | deps not synced; `torch` and `transformers` absent; weights absent | OV-Encoder dir exists but has no payload files | process RSS and tracemalloc available; torch memory unavailable | Sync/probe `envs/ov-encoder`; test `attn_implementation="eager"` or SDPA before runtime claims. |
| `llava_ov2` | partial | deps not synced; `torch`, `transformers`, video deps absent; ffmpeg absent; weights absent | LLaVA-OV2 dir exists but has no payload files | process RSS and tracemalloc available; torch memory unavailable | Install/verify ffmpeg, sync/probe `envs/llava-ov2`, then download weights before any generation. |
| `lmms_eval` | partial | deps not synced; adapter import blocked by missing deps such as `loguru`; benchmark deps absent; weights absent | model weights absent | process RSS and tracemalloc available; torch memory unavailable | Keep isolated; sync/probe only after model envs are validated. |
| `mps_probe` | partial / optional | optional env not synced; `numpy`, `PIL`, and `torch` absent | model weights absent | process RSS and tracemalloc available; MPS memory unavailable | Optional only; sync with torch extras later if a Mac probe is useful. |

## Detailed Results

### bridge-core

Status: `pass`

Verification:

```bash
cd envs/bridge-core
uv run pytest ../../projects/gaze-ov-bridge/tests
uv run python ../../scripts/profile_summary.py ../../artifacts/profiles/compat_*.json || true
```

Result:

- `35 passed`
- `profile_summary.py` parsed all five compatibility profile JSON files.

Readiness:

- Ready for Project A pure-Python selector/codec-artifact work.
- Ready for Project B pure-Python OV-direct geometry/artifact work.
- Not a model runtime environment.

### autogaze

Status: `partial`

Versions/imports:

- `autogaze`: importable from `external/AutoGaze` source path.
- `torch`: not installed.
- `torchvision`: not installed.
- `transformers`: not installed.
- `flash_attn`: not installed.
- `timm`, `hydra-core`, `av`, `imageio`, `numpy`, `PIL`: not installed in the unsynced probe env.

Source paths:

- `external/AutoGaze`: present.
- AutoGaze source mentions `gazing_pos` and `if_padded_gazing`.
- Upstream metadata declares `flash_attn`.
- Source mentions `sdpa`; eager fallback was not confirmed by this import-only probe.

Attention backend:

- `flash_attn` import: missing.
- Missing `flash_attn` is not a bridge-core failure.
- Runtime classification remains Linux/CUDA-oriented until an isolated AutoGaze probe proves SDPA/eager fallback is usable.

ffmpeg:

- Not available on current host.

Weights:

- `weights/checkpoints/AutoGaze`: exists.
- Payload file count: `0`.
- Manifest: absent.

Profiling:

- process RSS: available.
- tracemalloc: available.
- torch CUDA/MPS memory: unavailable because torch is not installed.

Next action:

- Download AutoGaze weights only when explicitly allowed.
- Sync/probe `envs/autogaze` on Linux/CUDA or with a confirmed non-FlashAttention path.

### ov_encoder

Status: `partial`

Versions/imports:

- `torch`: not installed.
- `transformers`: not installed.
- `numpy`, `PIL`: not installed in the unsynced probe env.
- OneVision-Encoder module imports fail because `torch`/`transformers` are absent.

Source paths:

- `external/OneVision-Encoder`: present.
- `external/LLaVA-OneVision-2/transformers_impl/onevision_encoder`: present.
- `patch_positions` path found.
- Source indicates SDPA/eager fallback hooks and FlashAttention support symbols.

Attention backend:

- Source supports an explicit `patch_positions` path.
- Source mentions/defines eager fallback and SDPA support indicators.
- Runtime fallback is not confirmed until `torch`/`transformers` are installed in `envs/ov-encoder`.

ffmpeg:

- Not available on current host. This is diagnostic for OV direct; not a pure geometry blocker.

Weights:

- `weights/checkpoints/onevision-encoder-large`: exists.
- Payload file count: `0`.
- Manifest: absent.

Profiling:

- process RSS: available.
- tracemalloc: available.
- torch CUDA/MPS memory: unavailable because torch is not installed.

Next action:

- Sync/probe `envs/ov-encoder`.
- Download weights only when explicitly allowed.
- Confirm `transformers==4.57.3` and `attn_implementation="eager"` or SDPA behavior before runtime work.

### llava_ov2

Status: `partial`

Versions/imports:

- `torch`: not installed.
- `transformers`: not installed.
- `decord`, OpenCV, `qwen-vl-utils`, `codec-video-prep`: not installed.
- HF custom-code imports fail because runtime dependencies such as `torch`, `transformers`, and `huggingface_hub` are absent.

Source paths:

- `external/LLaVA-OneVision-2`: present.
- `external/LLaVA-OneVision-2-8B-Instruct-code`: present.
- Codec processing path found.
- `image_grid_thw` and `patch_positions` source paths found.
- Source declares FlashAttention and SDPA support indicators and includes eager fallback references.

Attention backend:

- Source suggests SDPA/eager fallback exists.
- Runtime fallback is not confirmed until the isolated LLaVA-OV2 environment is synced.

ffmpeg:

- Not available on current host.
- This blocks codec backend tests.

Weights:

- `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct`: exists.
- Payload file count: `0`.
- Manifest: absent.

Profiling:

- process RSS: available.
- tracemalloc: available.
- torch CUDA/MPS memory: unavailable because torch is not installed.

Next action:

- Install/verify ffmpeg on Linux.
- Sync/probe `envs/llava-ov2`.
- Download LLaVA-OV2 weights only when explicitly allowed.
- Confirm processor import and attention backend before any generation.

### lmms_eval

Status: `partial`

Versions/imports:

- `lmms_eval`: importable from `external/lmms-eval` source path.
- `llava_onevision2` adapter import fails because runtime dependency `loguru` is absent.
- `torch`, `transformers`, `accelerate`, `datasets`, `evaluate`, OpenCV, `av`, and `qwen-vl-utils`: not installed in the unsynced probe env.

Source paths:

- `external/lmms-eval`: present.
- `llava_onevision2` adapter found.
- Adapter source mentions codec backend selection.
- Adapter source has latency/token hooks (`e2e_latency`, `total_tokens`, `avg_speed`).

Attention backend:

- Adapter defaults to `flash_attention_2`.
- CPU/MPS or non-FlashAttention behavior requires an explicit override/probe plan.

ffmpeg:

- Not available on current host.

Weights:

- Model weights are absent.

Profiling:

- process RSS: available.
- tracemalloc: available.
- torch CUDA/MPS memory: unavailable because torch is not installed.

Next action:

- Defer `lmms-eval` sync until AutoGaze, OV-Encoder, and LLaVA-OV2 model envs are validated.
- Do not run full benchmark until weights, ffmpeg, and attention backend are resolved.

### mps_probe

Status: `partial / optional`

Versions/imports:

- Platform: Darwin arm64.
- `numpy`: not installed in the unsynced optional env.
- `PIL`: not installed.
- `torch`: not installed.

MPS:

- MPS availability could not be checked because torch is not installed.
- This does not block Linux compatibility.

Weights:

- Model weights are absent.

Profiling:

- process RSS: available.
- tracemalloc: available.
- torch MPS memory: unavailable because torch is not installed.

Next action:

- Optional only: sync `envs/mps-probe` with torch extras later if lightweight local MPS diagnostics are useful.

## Cross-Cutting Findings

- HF cache paths are correctly under `weights/`:
  - `HF_HOME=/Users/mrc/Documents/VTC/weights/hf_home`
  - `HF_HUB_CACHE=/Users/mrc/Documents/VTC/weights/hf_home/hub`
- External source paths are present for AutoGaze, LLaVA-OV2, OneVision-Encoder custom code, and `lmms-eval`.
- All checkpoint directories exist but contain no model payload files.
- `ffmpeg` is still absent on the current host and still unverified on Linux.
- Profile JSON outputs are valid and summarizable.

## Readiness Decision

Project A worktree:

- Pure-Python Project A bridge work can start.
- LLaVA-OV2 model/codec runtime work remains blocked by missing weights, missing ffmpeg, unsynced `envs/llava-ov2`, and unverified attention backend.

Project B worktree:

- Pure-Python Project B bridge work can start.
- OV-Encoder model runtime work remains blocked by missing weights, unsynced `envs/ov-encoder`, and unverified attention backend.

lmms-eval worktree:

- Source-audit and planning work can start.
- Full benchmark work remains blocked by missing model runtimes, missing weights, missing ffmpeg, and unsynced `envs/lmms-eval`.
