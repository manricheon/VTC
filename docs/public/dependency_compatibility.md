# Dependency Compatibility Audit Plan

This audit is for `projects/gaze-ov-bridge` before any model integration. It follows the repository policy that Linux is the official target, `uv` is the package/environment manager, MacBook/MPS is best-effort only, and AutoGaze, OneVision-Encoder, LLaVA-OV2, and `lmms-eval` must not be forced into one Python environment.

No external repositories, model weights, heavy dependencies, or model inference are required for this audit document.

## Source Status

Primary sources checked:

- AutoGaze project page and repository: <https://autogaze.github.io/> and <https://github.com/NVlabs/AutoGaze>
- AutoGaze package metadata: <https://github.com/NVlabs/AutoGaze/blob/main/pyproject.toml>
- AutoGaze paper: <https://arxiv.org/abs/2603.12254>
- OneVision-Encoder paper: <https://arxiv.org/abs/2602.08683>
- OneVision-Encoder Hugging Face repos:
  - <https://huggingface.co/lmms-lab-encoder/onevision-encoder-large-lang>
  - <https://huggingface.co/lmms-lab-encoder/onevision-encoder-large-tf57>
  - <https://huggingface.co/lmms-lab-encoder/onevision-encoder-large-lang-tf57>
- LLaVA-OneVision-2 paper: <https://arxiv.org/abs/2605.25979>
- LLaVA-OneVision-2 Hugging Face repo: <https://huggingface.co/lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct>
- `lmms-eval` package metadata: <https://raw.githubusercontent.com/EvolvingLMMs-Lab/lmms-eval/main/pyproject.toml>
- FlashAttention repository: <https://github.com/Dao-AILab/flash-attention>
- Hugging Face Transformers attention documentation: <https://huggingface.co/docs/transformers/main/en/perf_infer_gpu_one>
- `codec-video-prep` PyPI metadata: <https://pypi.org/project/codec-video-prep/>

Where public package metadata is not visible, this document records the current working requirement as an integration assumption to verify later with source audit and `uv` probe environments.

## Known Version Requirements

### AutoGaze

Public `pyproject.toml` currently lists:

- Python `>=3.8`
- `torch`
- `torchvision`
- `flash_attn`
- `hydra-core>=1.3.2`
- `wandb`
- `loguru`
- `timm>=1.0.15`
- `tqdm`
- `transformers~=4.51`
- `pillow`
- `numpy`
- `omegaconf`
- `matplotlib`
- `einops`
- `av`
- `imageio`
- dev extras: `pytest>=8.0.0`, `pytest-cov>=4.1.0`, `pytest-mock>=3.12.0`

The AutoGaze README installation path creates a Python 3.11 conda environment, installs CUDA toolkit 12.8, installs `uv`, then runs `uv pip install -e .`. Treat the public AutoGaze runtime as Linux/CUDA-oriented until proven otherwise.

Bridge implication: `envs/bridge-core` must not depend on AutoGaze. AutoGaze should generate artifacts in `envs/autogaze`; bridge code consumes serialized JSON/NPY outputs.

### OneVision-Encoder

Known working target for this project:

- `transformers==4.57.3` recommended.
- `transformers>=5.0.0` currently unsupported for the direct OV-Encoder path until source audit proves otherwise.
- Patch size: 14.
- Canonical video input: 224.
- Native grid: `224 / 14 = 16`.
- 3D RoPE is part of the model design.
- The `patch_positions` path must be considered for irregular, sparse token layouts.

Public metadata confirms Hugging Face custom-code `onevision_encoder` repos, including `onevision-encoder-large`, `onevision-encoder-large-lang`, and `*-tf57` variants. The paper describes codec patchification and shared 3D RoPE for irregular token layouts.

Bridge implication: Project B must use a dedicated `envs/ov-encoder` environment. It should consume OV-direct artifacts produced by bridge-core and must not import AutoGaze directly.

### LLaVA-OV2

Known working target for this project:

- `transformers>=5.7.0`
- `torch>=2.4`
- `decord`
- `codec-video-prep`
- `opencv-python`
- system `ffmpeg`

Public metadata confirms the Hugging Face custom-code `llava_onevision2` architecture for `lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct`. The LLaVA-OneVision-2 paper describes a native OneVision-Encoder, windowed attention, codec-stream tokenization, codec canvases, and shared 3D RoPE. `codec-video-prep` metadata describes codec-aware preprocessing, patched FFmpeg builds, H.264/HEVC/VP9 bitcost extraction, `patch=14`, canvas outputs, and metadata/NPY outputs.

Bridge implication: Project A must use a dedicated `envs/llava-ov2` environment. It should consume codec-compatible artifacts and should not import AutoGaze.

### lmms-eval `llava-onevision2`

Public `lmms-eval` metadata shows a broad dependency surface:

- Python `>=3.10`
- `accelerate>=0.29.1`
- `datasets>=2.19.0`
- `evaluate>=0.4.0`
- `numpy>=1.26.4`
- `peft>=0.2.0`
- `torch>=2.1.0`
- `torchvision>=0.16.0`
- `timm`
- `einops`
- `opencv-python-headless`
- `av<16.0.0`
- `transformers>=4.39.2`
- `transformers-stream-generator`
- `qwen-vl-utils>=0.0.14`
- `sentence_transformers`
- `wandb==0.25.0`
- many benchmark, metric, server, API, audio, and document dependencies.
- optional video extras include `torchcodec>=0.3.0`.
- optional legacy video extras include `decord` on non-Darwin platforms and `eva-decord` on Darwin with Python `<3.12`.

Likely conflicts:

- The broad `transformers>=4.39.2` range can resolve to versions incompatible with AutoGaze (`~=4.51`), OV-Encoder (`==4.57.3` target), or LLaVA-OV2 (`>=5.7.0` target) unless pinned per environment.
- Video backends (`av`, `torchcodec`, `decord`, OpenCV) can conflict at the system-library layer.
- Benchmark tooling brings API clients, metrics packages, and optional UI/server dependencies that do not belong in bridge-core.

Bridge implication: `lmms-eval` must remain isolated in `envs/lmms-eval`.

## Risk Analysis

- A single unified environment is risky and should not be attempted for initial integration.
- `transformers` requirements conflict:
  - AutoGaze: `transformers~=4.51`
  - OV-Encoder direct path: `transformers==4.57.3` recommended, `>=5.0.0` unsupported until verified
  - LLaVA-OV2: `transformers>=5.7.0`
  - `lmms-eval`: broad `transformers>=4.39.2`, likely requiring task-specific pins
- `flash_attn` is likely hardware- and toolchain-specific. It requires source audit before any model path can rely on it. It must not be required for bridge-core.
- FlashAttention public docs emphasize Linux plus CUDA or ROCm toolchains, and CUDA FlashAttention-2 support is tied to GPU architecture, dtype, and CUDA version. Treat `flash_attn` paths as Linux GPU paths unless source audit proves fallback works.
- `ffmpeg`, `decord`, `av`, `torchcodec`, OpenCV, and codec preprocessing should remain optional until codec/backend tests.
- `lmms-eval` has a large benchmark dependency surface and must be isolated.
- MPS tests are allowed only as best-effort probes. Linux remains the official target and the only platform for compatibility decisions.

## Environment Split Proposal

### `envs/bridge-core`

Purpose:

- Pure Python bridge logic.
- Synthetic tests.
- JSON/NPY artifact validation.
- Profiling schema validation.

Allowed dependencies:

- `numpy`
- `pillow`
- `pytest`
- stdlib profiling and metadata utilities.

Disallowed in bridge-core:

- `torch`
- `transformers`
- `flash_attn`
- AutoGaze
- OneVision-Encoder
- LLaVA-OV2
- `lmms-eval`
- real model weights
- real model inference

### `envs/autogaze`

Purpose:

- Run actual AutoGaze output generation after source audit.
- Serialize AutoGaze outputs to `artifacts/autogaze/<video_id>/`.

Expected dependency family:

- AutoGaze package metadata dependencies, including `torch`, `torchvision`, `transformers~=4.51`, `flash_attn`, `timm`, `hydra-core`, `av`, and `imageio`.

### `envs/ov-encoder`

Purpose:

- Run OneVision-Encoder direct forward path after source audit.
- Consume Project B direct artifacts from bridge-core.

Expected dependency family:

- `transformers==4.57.3`
- torch stack selected for Linux target.
- OneVision-Encoder custom code.

### `envs/llava-ov2`

Purpose:

- Run LLaVA-OV2 processor/backend/generation after source audit.
- Consume Project A codec-compatible artifacts.

Expected dependency family:

- `transformers>=5.7.0`
- `torch>=2.4`
- `codec-video-prep`
- `decord`
- `opencv-python`
- system `ffmpeg`

### `envs/lmms-eval`

Purpose:

- Benchmark execution.
- Later `llava-onevision2` evaluation.

Expected dependency family:

- Isolated `lmms-eval` install with benchmark-specific pins.
- Optional video extras selected explicitly.

### `envs/mps-probe`

Purpose:

- Optional Mac/MPS import checks and lightweight runtime probes.
- No official compatibility decision should depend solely on this environment.

Expected dependency family:

- Only packages proven to import on Mac/MPS without `flash_attn` hard failure.
- No model downloads during initial probes.

## flash_attn Audit Plan

Before installing or patching model dependencies, search each external source tree after it is explicitly cloned:

```bash
rg -n "flash_attn|flash_attention|flash_attention_2|attn_implementation|sdpa|eager" external/<repo-or-package>
```

For each model path, answer:

1. Is `flash_attn` imported at module import time?
2. Is `flash_attn` required in package metadata only, or required by executable code?
3. Does model loading accept `attn_implementation="sdpa"` or `attn_implementation="eager"`?
4. Does the code hard-code `"flash_attention_2"`?
5. Does fallback preserve required outputs for the bridge path?
6. Does fallback work on CPU?
7. Does fallback work on MPS?

Classification:

- If `flash_attn` is optional and `sdpa` or `eager` works, include CPU/MPS import-only and tiny-runtime probes.
- If `flash_attn` is mandatory at top level, classify that model path as Linux/CUDA-only until upstream changes or a deliberate patch plan exists.
- If `flash_attn` is mandatory only for performance paths, keep fallback path as the default for bridge probes.

Do not patch around `flash_attn` until source audit confirms the safest path.

## Compatibility Probes To Run Later

These are future probes only. Do not run them during initial setup.

For each environment:

1. Create a separate `uv` project or lock file under the matching `envs/<name>/` directory.
2. Run `uv lock` separately.
3. Run `uv sync` separately.
4. Print versions where applicable:

```bash
python - <<'PY'
import importlib.metadata as md

for name in [
    "torch",
    "torchvision",
    "transformers",
    "flash-attn",
    "av",
    "imageio",
    "opencv-python",
    "opencv-python-headless",
    "decord",
    "torchcodec",
    "codec-video-prep",
    "lmms-eval",
]:
    try:
        print(f"{name}=={md.version(name)}")
    except md.PackageNotFoundError:
        print(f"{name}: not installed")
PY
```

5. Print system tools where applicable:

```bash
ffmpeg -version
```

6. Run import-only probes.
7. Run no model downloads in the initial probe.
8. Set Hugging Face cache/download paths to `weights/` before any later download-enabled probe.
9. Save results under `artifacts/compat/<env_name>/`.

Suggested outputs:

- `artifacts/compat/<env_name>/uv_lock_summary.txt`
- `artifacts/compat/<env_name>/package_versions.json`
- `artifacts/compat/<env_name>/system_versions.json`
- `artifacts/compat/<env_name>/import_probe.json`
- `artifacts/compat/<env_name>/attention_probe.json`

## Artifact Exchange Decision

Use JSON/NPY files between environments. Do not import model packages across environments.

AutoGaze output artifacts:

- `artifacts/autogaze/<video_id>/gazing_pos.npy`
- `artifacts/autogaze/<video_id>/if_padded_gazing.npy`
- `artifacts/autogaze/<video_id>/decoded_entries.json`

Project A codec-compatible artifacts:

- `artifacts/project_a_codec/<video_id>/selected_blocks.json`
- `artifacts/project_a_codec/<video_id>/src_positions.npy`
- `artifacts/project_a_codec/<video_id>/stats.json`

Project B OV-direct artifacts:

- `artifacts/project_b_ov_direct/<video_id>/patches.npy`
- `artifacts/project_b_ov_direct/<video_id>/patch_positions.npy`
- `artifacts/project_b_ov_direct/<video_id>/stats.json`

## Profiling Compatibility

- bridge-core profiling must use stdlib and NumPy only.
- torch memory profiling is optional and collected only when torch is installed.
- CUDA profiling is valid only in CUDA environments.
- MPS profiling is best-effort only.
- Profiling outputs go under `artifacts/profiles/` or per-run `out/` directories.
- The profile schema must be shared across Project A, Project B, and `lmms-eval` runners.

Minimum shared profile fields:

- `run_id`
- `git_commit`
- `project`
- `environment_name`
- `platform`
- `python_version`
- `package_versions`
- `input_video_id`
- `input_artifacts`
- `output_artifacts`
- `timings`
- `token_counts`
- `compression_ratios`
- `peak_cpu_memory`
- `cuda_memory`
- `mps_memory`
- `notes`

Memory collection policy:

- CPU: use stdlib first, such as `resource` on Linux where available.
- NumPy: record array shapes, dtypes, and byte counts.
- torch: collect only when torch is installed.
- CUDA: collect only when `torch.cuda.is_available()` is true in a CUDA environment.
- MPS: collect only in best-effort MPS probes and never treat MPS measurements as official Linux performance.

## Decision Rules

- If AutoGaze and LLaVA-OV2 `transformers` requirements conflict, keep separate environments.
- If OneVision-Encoder and LLaVA-OV2 `transformers` requirements conflict, keep separate environments.
- If AutoGaze and OneVision-Encoder `transformers` requirements conflict, keep separate environments.
- AutoGaze output should be serialized to artifacts and consumed by bridge-core.
- LLaVA-OV2 should consume codec-compatible artifacts, not import AutoGaze directly.
- OV-Encoder should consume OV-direct artifacts, not import AutoGaze directly.
- `lmms-eval` should run benchmark adapters in `envs/lmms-eval`, not in bridge-core or model-generation environments.
- If `flash_attn` is mandatory for a model import path, classify that path as Linux/CUDA-only.
- If `sdpa` or `eager` fallback works, prefer fallback for CPU/MPS-safe probes and reserve `flash_attn` for Linux GPU performance runs.
- If codec/video libraries conflict, isolate the codec/backend test in `envs/llava-ov2` or a dedicated future codec probe environment.

## Initial Conclusion

The project should proceed with separate environments and artifact exchange. The first implementation work should stay in `envs/bridge-core`, using synthetic tests and JSON/NPY artifacts. Real model integrations should wait until source audits, `uv` locks, import-only probes, and attention fallback probes have been recorded under `artifacts/compat/`.
