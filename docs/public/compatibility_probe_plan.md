# Compatibility Probe Plan

This plan defines isolated, import-only compatibility probes for AutoGaze, OneVision-Encoder, LLaVA-OV2, `lmms-eval`, and optional Mac/MPS checks.

The probes do not download weights, clone repositories, run full inference, or combine model dependency stacks into one environment. Linux remains the official target. Mac/MPS probe results are best-effort diagnostics only.

## Probe Environments

Each model family has its own `uv` project:

- `envs/autogaze`: AutoGaze output generation environment.
- `envs/ov-encoder`: OneVision-Encoder direct forward environment.
- `envs/llava-ov2`: LLaVA-OV2 processor/backend/generation environment.
- `envs/lmms-eval`: benchmark environment.
- `envs/mps-probe`: optional Mac/MPS diagnostics.

These environments intentionally remain separate because their `transformers`, video backend, and attention dependencies differ. `bridge-core` stays pure Python and does not import `torch`, `transformers`, AutoGaze, OneVision-Encoder, LLaVA-OV2, or `lmms-eval`.

## Running Probes

The aggregate helper prints commands by default and does not install dependencies:

```bash
bash scripts/run_compat_probes.sh
```

To run probes in already-synced environments without triggering a dependency sync:

```bash
RUN_UV_PROBES=1 bash scripts/run_compat_probes.sh
```

To include the optional MPS probe:

```bash
RUN_UV_PROBES=1 RUN_OPTIONAL_MPS=1 bash scripts/run_compat_probes.sh
```

Individual probes can also be run from their matching environment:

```bash
cd envs/autogaze
uv run --no-sync python ../../scripts/probe_autogaze_env.py

cd ../ov-encoder
uv run --no-sync python ../../scripts/probe_ov_encoder_env.py

cd ../llava-ov2
uv run --no-sync python ../../scripts/probe_llava_ov2_env.py

cd ../lmms-eval
uv run --no-sync python ../../scripts/probe_lmms_eval_env.py

cd ../mps-probe
uv run --no-sync python ../../scripts/probe_mps_env.py
```

`--no-sync` is intentional for the first probe pass. It records what is currently importable without installing heavy dependencies or touching model weights.

## Outputs

Every probe writes:

- `artifacts/compat/<env>_env.json`
- `artifacts/profiles/compat_<env>.json`

The `artifacts/` tree is ignored by git. Probe outputs are runtime evidence, not committed source.

## What Each Probe Validates

### AutoGaze

`scripts/probe_autogaze_env.py` checks:

- package versions for `torch`, `torchvision`, `transformers`, `flash-attn`, `timm`, `hydra-core`, `av`, `imageio`, `numpy`, and `pillow`
- import status for AutoGaze source and related dependencies
- `ffmpeg` availability
- source mentions for `flash_attn`, `attn_implementation`, `sdpa`, `eager`, `gazing_pos`, and `if_padded_gazing`
- process RSS, tracemalloc, and optional torch CUDA/MPS memory metrics

AutoGaze upstream metadata currently declares `flash_attn`. Missing `flash_attn` is a compatibility result, not a bridge-core failure. If later source/import probes prove `flash_attn` is mandatory, AutoGaze actual generation is classified as Linux/CUDA-only.

### OneVision-Encoder

`scripts/probe_ov_encoder_env.py` checks:

- `torch` and `transformers` versions
- import status for OneVision-Encoder custom configuration/modeling modules
- source mentions for `patch_positions`, `_supports_sdpa`, `_supports_flash_attn`, `eager`, and Transformers attention dispatch
- `ffmpeg` availability as a diagnostic
- process RSS, tracemalloc, and optional torch CUDA/MPS memory metrics

The expected direct-path target is `transformers==4.57.3`. `transformers>=5.0.0` remains unsupported for this path until a source probe proves otherwise.

### LLaVA-OV2

`scripts/probe_llava_ov2_env.py` checks:

- versions/imports for `torch`, `transformers`, `decord`, OpenCV, `qwen-vl-utils`, and `codec-video-prep`
- `ffmpeg` availability
- Hugging Face custom-code source mentions for codec processing, `image_grid_thw`, `patch_positions`, `_supports_sdpa`, `_supports_flash_attn`, and eager attention
- process RSS, tracemalloc, and optional torch CUDA/MPS memory metrics

The LLaVA-OV2 source audit suggests SDPA/eager support exists, but this must be confirmed in the isolated environment before relying on CPU or MPS probes.

### lmms-eval

`scripts/probe_lmms_eval_env.py` checks:

- versions/imports for `lmms-eval`, `torch`, `transformers`, `accelerate`, `datasets`, `evaluate`, OpenCV, `av`, and `qwen-vl-utils`
- `ffmpeg` availability
- source mentions for the `llava_onevision2` adapter, `attn_implementation`, `flash_attention_2`, codec backend selection, latency hooks, and token counters
- process RSS, tracemalloc, and optional torch CUDA/MPS memory metrics

The current source snapshot shows the `llava_onevision2` adapter defaults to `attn_implementation="flash_attention_2"`. Treat that default as Linux/CUDA-oriented unless a later probe confirms an override path.

### MPS

`scripts/probe_mps_env.py` checks:

- platform and machine metadata
- `torch`, `numpy`, and `PIL` import status
- torch MPS built/available flags when torch is installed
- process RSS, tracemalloc, and optional torch MPS memory metrics

MPS failures do not block Linux compatibility. MPS results are only best-effort local diagnostics.

## Interpreting `flash_attn` Failures

`flash_attn` is not required for `bridge-core`. A failed `flash_attn` import in a model-specific probe means one of:

- the current environment has not installed the CUDA-oriented optional package
- the local platform cannot build or load it
- the model path needs `attn_implementation="sdpa"` or `"eager"`
- the source path is Linux/CUDA-only until a fallback is verified

Do not patch around `flash_attn` based only on import failure. First confirm whether the relevant model code imports it at module import time, whether package metadata only declares it, and whether SDPA/eager fallback preserves the bridge path.

## Profiling Capability Results

Every probe records whether it can collect:

- process peak RSS through stdlib `resource`
- Python allocation peak through stdlib `tracemalloc`
- torch CUDA memory if torch is installed and CUDA is available
- torch MPS memory if torch is installed and MPS is available

`tracemalloc` is Python allocation tracking, not total native memory. CUDA metrics are valid only in CUDA environments. MPS metrics are best-effort and not official compatibility evidence.

## Decision Rules

- If AutoGaze and LLaVA-OV2 `transformers` requirements conflict, keep separate environments.
- If OneVision-Encoder and LLaVA-OV2 `transformers` requirements conflict, keep separate environments.
- AutoGaze outputs must be serialized to `artifacts/autogaze/<video_id>/` and consumed by bridge-core.
- LLaVA-OV2 must consume Project A codec-compatible artifacts and must not import AutoGaze directly.
- OV-Encoder must consume Project B OV-direct artifacts and must not import AutoGaze directly.
- `lmms-eval` remains isolated until benchmark-specific profiling hooks are added.
